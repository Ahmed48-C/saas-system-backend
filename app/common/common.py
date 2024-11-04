from datetime import datetime
import threading


def add_timestamp_to_image_file(file):
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    file_ext = "." + file.split('.')[-1]
    filename = file[:-len(file_ext)]
    new_filename = filename + "_" + date + file_ext
    return new_filename


def upload_base64_image_to_cloudniary(base64_image_data, filename):
    import cloudinary
    import cloudinary.uploader
    import os

    # Configuration
    cloudinary.config(
        cloud_name = "dblq0iusj",
        api_key = "889146747641355",
        api_secret = "tKnOAQ4TpL-LWwiCVEEz9cotNz8",
        secure=True
    )

    def upload_base64_image(base64_data, filename, format="png"):
        try:
            # Upload the image to Cloudinary
            filename, _ = os.path.splitext(filename)
            response = cloudinary.uploader.upload(base64_data, public_id=filename, format=format)
            print("Upload successful!")
            print("URL:", response['url'])
            return response
        except Exception as e:
            print("Error uploading image:", e)

    # Usage
    response = upload_base64_image(base64_image_data, filename)


def upload_image_by_thread(image_file, image):
    thread = threading.Thread(target=upload_base64_image_to_cloudniary, args=(image_file, image))
    thread.start()
