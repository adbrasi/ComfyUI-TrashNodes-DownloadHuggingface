import os
import subprocess

class DownloadLinkChecker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LINK": ("STRING", {}),
                "OUTPUT": ("STRING", {}),
                "START_NUMBER": ("INT", {"default": 0}),
                "END_NUMBER": ("INT", {"default": 130})
            },
            "optional": {
                "SYMLINK_DIRECTORY": ("STRING", {}),
                "huggingface_token_for_private_repo": ("STRING", {})
            }
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "check_download_link"
    CATEGORY = "examples"

    def check_download_link(self, LINK, OUTPUT, START_NUMBER, END_NUMBER, SYMLINK_DIRECTORY=None, huggingface_token_for_private_repo=None):
        cleaned_link = LINK.split("?download=true")[0]

        # Verifica se a pasta de saída fornecida pelo usuário é válida
        if os.path.isdir(OUTPUT):
            pasta = OUTPUT
        else:
            return []

        file_path = os.path.join(pasta, "links.txt")

        # Gerar links
        links = self.generate_links(cleaned_link, START_NUMBER, END_NUMBER)

        # Escrever os links em um arquivo
        with open(file_path, "w") as file:
            file.writelines(links)

        # Baixar os arquivos usando wget
        wget_command = ["wget", "-P", pasta, "-i", file_path]

        if huggingface_token_for_private_repo:
            wget_command.extend(["--header", f"Authorization: Bearer {huggingface_token_for_private_repo}"])

        try:
            subprocess.run(wget_command, check=True)
            status_message = "Download concluído com sucesso."
        except subprocess.CalledProcessError as e:
            status_message = f"Erro durante o download: {str(e)}"

        # Listar os arquivos na pasta de saída
        output_files = os.listdir(pasta)

        # Se um diretório de link simbólico for fornecido, criar links simbólicos
        # Se um diretório de link simbólico for fornecido, criar links simbólicos
        if SYMLINK_DIRECTORY:
            for file in output_files:
                source_file_path = os.path.join(pasta, file)
                destination_file_path = os.path.join(SYMLINK_DIRECTORY, file)
                if not os.path.exists(destination_file_path):
                    os.symlink(source_file_path, destination_file_path)
                else:
                    print(f"O arquivo {file} já existe no diretório de destino.")


        return output_files

    def generate_links(self, cleaned_link, start=0, end=130):
        links = []
        for i in range(start, end + 1):
            number_str = cleaned_link.split('-')[-1].split('.')[0]
            padded_number = number_str.zfill(6)
            new_link = cleaned_link.replace(number_str, "{:06d}".format(i))
            links.append(new_link + "\n")
        return links

class ShowFileNames:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_names": ("LIST", {"items": ("STRING", {})})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "show_file_names"
    OUTPUT_NODE = True

    CATEGORY = "utils"

    def show_file_names(self, file_names):
        file_names_text = "\n".join(file_names)
        return {"ui": {"text": file_names_text}, "result": (file_names_text,)}


NODE_CLASS_MAPPINGS = {
    "DownloadLinkChecker": DownloadLinkChecker,
    "ShowFileNames": ShowFileNames
}
