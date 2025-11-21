import cloudinary
import cloudinary.uploader
from config import settings
from io import BytesIO

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_csv_to_cloudinary(file_content: bytes, filename: str) -> str:
    """
    Upload CSV file to Cloudinary and return the URL
    Args:
        file_content: Bytes content of the CSV file
        filename: Original filename
    Returns:
        Cloudinary secure URL
    """
    try:
        # Upload to Cloudinary as raw file
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="raw",  # For non-image files
            folder="meta_ads_csv",  # Organize in folder
            public_id=filename.replace('.csv', ''),  # Remove extension for public_id
            overwrite=True,
            format="csv"
        )

        return upload_result['secure_url']

    except Exception as e:
        raise Exception(f"Failed to upload to Cloudinary: {str(e)}")

def download_csv_from_cloudinary(url: str) -> str:
    """
    Download CSV content from Cloudinary URL
    Args:
        url: Cloudinary secure URL
    Returns:
        CSV content as string
    """
    try:
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    except Exception as e:
        raise Exception(f"Failed to download from Cloudinary: {str(e)}")

def delete_csv_from_cloudinary(url: str) -> bool:
    """
    Delete CSV file from Cloudinary
    Args:
        url: Cloudinary secure URL
    Returns:
        True if successful
    """
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/{cloud_name}/raw/upload/{version}/meta_ads_csv/{public_id}.csv
        parts = url.split('/')
        public_id_with_ext = parts[-1]  # e.g., "filename.csv"
        public_id = public_id_with_ext.replace('.csv', '')
        full_public_id = f"meta_ads_csv/{public_id}"

        cloudinary.uploader.destroy(full_public_id, resource_type="raw")
        return True

    except Exception as e:
        print(f"Warning: Failed to delete from Cloudinary: {str(e)}")
        return False
