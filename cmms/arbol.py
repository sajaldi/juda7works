import os

def print_tree(root, indent=""):
    """
    Imprime recursivamente el árbol de directorios a partir de la ruta 'root'
    utilizando el string 'indent' para la indentación.
    """
    # Obtenemos y ordenamos los elementos de la carpeta
    items = sorted(os.listdir(root))
    total = len(items)
    
    for index, item in enumerate(items):
        path = os.path.join(root, item)
        # Determinar el conector a usar según si es el último elemento
        if index == total - 1:
            connector = "└── "
            next_indent = indent + "    "
        else:
            connector = "├── "
            next_indent = indent + "│   "
        
        print(indent + connector + item)
        
        # Si el elemento es un directorio, se llama recursivamente
        if os.path.isdir(path):
            print_tree(path, next_indent)

if __name__ == "__main__":
    # Puedes cambiar '.' por cualquier otro directorio que quieras mostrar
    root_dir = "."
    
    # Imprime el directorio raíz y luego su árbol
    print(root_dir)
    print_tree(root_dir)