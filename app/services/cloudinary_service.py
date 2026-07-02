import cloudinary.uploader


class CloudinaryService:

    @staticmethod
    def subir_imagen(archivo, carpeta):

        resultado = cloudinary.uploader.upload(

            archivo,

            folder=carpeta

        )

        return resultado["secure_url"]


    @staticmethod
    def subir_video(archivo, carpeta):

        resultado = cloudinary.uploader.upload(

            archivo,

            resource_type="video",

            folder=carpeta

        )

        return resultado["secure_url"]