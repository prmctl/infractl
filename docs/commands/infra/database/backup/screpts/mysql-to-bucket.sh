#!/bin/bash

# مسیر فایل لاگ
LOG_FILE="/home/devops/DB/bucket/upload.log"

# پاک کردن محتوای لاگ در ابتدای اجرا
> "$LOG_FILE"

# نوشتن هدر لاگ
server_name=$(cat /etc/hostname)
echo "$server_name" > "$LOG_FILE"
echo "------------------------" >> "$LOG_FILE"

# ثبت زمان شروع
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "Start time: $START_TIME" >> "$LOG_FILE"
echo "------------------------" >> "$LOG_FILE"


# مسیر اسکریپت backup اولیه (script.sh)
SCRIPT_PATH="/home/devops/DB/script.sh"

# اجرای script.sh و بررسی موفقیت آن
echo "Running initial backup script..."
bash "$SCRIPT_PATH"

# بررسی وضعیت خروجی script.sh
if [ $? -ne 0 ]; then
    echo "Error: script.sh failed. Exiting backup process."
    exit 1
fi

echo "script.sh executed successfully. Proceeding with upload..."

# مسیر فایل تنظیمات
CONFIG_FILE="/home/devops/DB/bucket/config/backupConfig.ini"



# بررسی وجود فایل تنظیمات
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file not found at $CONFIG_FILE." | tee -a "$LOG_FILE"
  exit 1
fi

# خواندن مقدار uploadService
UPLOAD_SERVICE=$(grep -oP '(?<=uploadService=")[^"]*' "$CONFIG_FILE")
echo "Upload Service: $UPLOAD_SERVICE" | tee -a "$LOG_FILE"

# بررسی مقدار uploadService
if [ "$UPLOAD_SERVICE" != "MINIO" ]; then
  echo "Upload service is not set to 'MINIO'. Exiting." | tee -a "$LOG_FILE"
  exit 0
fi

# خواندن اطلاعات اتصال برای MINIO
ACCESS_KEY=$(grep -oP '(?<=AWS_KEY=")[^"]*' "$CONFIG_FILE")
SECRET_KEY=$(grep -oP '(?<=AWS_SECRET_KEY=")[^"]*' "$CONFIG_FILE")
ENDPOINT=$(grep -oP '(?<=ENDPOINT=")[^"]*' "$CONFIG_FILE")
BUCKET_NAME=$(grep -oP '(?<=bucketName=")[^"]*' "$CONFIG_FILE")

# نوشتن اطلاعات اولیه در لاگ
echo "Bucket: $BUCKET_NAME" >> "$LOG_FILE"

# مسیر بکاپ
BACKUP_DIR="/home/devops/DB/backup"

# پیدا کردن جدیدترین فایل با پسوندهای مختلف
FILE_PATH=$(ls -t ${BACKUP_DIR}/*.{zip,tgz,log} 2>/dev/null | head -n 1)

# بررسی وجود فایل
if [ -z "$FILE_PATH" ]; then
  echo "Error: No backup files found in ${BACKUP_DIR}." | tee -a "$LOG_FILE"
  exit 1
fi

OBJECT_KEY=$(basename "$FILE_PATH") # نام فایل در فضای ذخیره‌سازی

# تعیین نوع محتوا بر اساس فرمت فایل
case "$FILE_PATH" in
  *.zip) CONTENT_TYPE="application/zip" ;;
  *.tgz) CONTENT_TYPE="application/gzip" ;;
  *.log) CONTENT_TYPE="text/plain" ;;
  *) echo "Unknown file format! Exiting." | tee -a "$LOG_FILE"; exit 1 ;;
esac

# نوشتن اطلاعات فایل در لاگ
FILE_SIZE=$(stat -c%s "$FILE_PATH")
echo "DB File: $OBJECT_KEY" >> "$LOG_FILE"
echo "File size: $(($FILE_SIZE / 1024)) KB" >> "$LOG_FILE"



# تاریخ و امضا برای آپلود
DATE=$(date -u +"%a, %d %b %Y %H:%M:%S GMT")
STRING_TO_SIGN="PUT\n\n${CONTENT_TYPE}\n${DATE}\n/${BUCKET_NAME}/${OBJECT_KEY}"
SIGNATURE=$(echo -en "$STRING_TO_SIGN" | openssl sha1 -hmac "$SECRET_KEY" -binary | base64)

# ارسال فایل با curl و محاسبه پراگرس
HTTP_RESPONSE=$(curl --progress-bar -w "%{http_code}" -o /dev/null -X PUT \
  -H "Host: $(echo $ENDPOINT | awk -F[/:] '{print $4}')" \
  -H "Date: ${DATE}" \
  -H "Content-Type: ${CONTENT_TYPE}" \
  -H "Authorization: AWS ${ACCESS_KEY}:${SIGNATURE}" \
  --data-binary @"${FILE_PATH}" \
  "${ENDPOINT}/${BUCKET_NAME}/${OBJECT_KEY}")

# بررسی وضعیت آپلود
if [ "$HTTP_RESPONSE" -eq 200 ]; then
  echo -e "\nFile uploaded successfully to ${BUCKET_NAME}/${OBJECT_KEY}." | tee -a "$LOG_FILE"

  # دریافت متادیتا از S3
  HEAD_DATE=$(date -u +"%a, %d %b %Y %H:%M:%S GMT")
  HEAD_STRING_TO_SIGN="HEAD\n\n\n${HEAD_DATE}\n/${BUCKET_NAME}/${OBJECT_KEY}"
  HEAD_SIGNATURE=$(echo -en "$HEAD_STRING_TO_SIGN" | openssl sha1 -hmac "$SECRET_KEY" -binary | base64)

  RESPONSE=$(curl -s -I \
    -H "Host: $(echo $ENDPOINT | awk -F[/:] '{print $4}')" \
    -H "Date: ${HEAD_DATE}" \
    -H "Authorization: AWS ${ACCESS_KEY}:${HEAD_SIGNATURE}" \
    "${ENDPOINT}/${BUCKET_NAME}/${OBJECT_KEY}")

  UPLOADED_SIZE=$(echo "$RESPONSE" | grep -i "Content-Length" | awk '{print $2}' | tr -d '\r')

  if [ "$FILE_SIZE" -eq "$UPLOADED_SIZE" ]; then
    echo "File verified successfully. Sizes match." | tee -a "$LOG_FILE"
    rm -f "$FILE_PATH"
    if [ $? -eq 0 ]; then
      echo "File $FILE_PATH deleted successfully." | tee -a "$LOG_FILE"
    else
      echo "Error deleting file $FILE_PATH." | tee -a "$LOG_FILE"
    fi
  else
    echo "File size mismatch! Original: $FILE_SIZE, Uploaded: $UPLOADED_SIZE" | tee -a "$LOG_FILE"
    echo "File not deleted." | tee -a "$LOG_FILE"
  fi
else
  echo -e "\nError uploading file. HTTP Response: $HTTP_RESPONSE. File not deleted." | tee -a "$LOG_FILE"
fi

# ثبت زمان پایان
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "End time: $END_TIME" >> "$LOG_FILE"
echo "------------------------" >> "$LOG_FILE"

# Run Telegram notification script without sudo fallback
TELEGRAM_SCRIPT="/home/devops/DB/bucket/DBBackupTelegram.sh"
if command -v sudo &>/dev/null; then
  sudo bash "$TELEGRAM_SCRIPT" || bash "$TELEGRAM_SCRIPT"
else
  bash "$TELEGRAM_SCRIPT"
fi