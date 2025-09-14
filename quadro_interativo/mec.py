from anastruct import SystemElements

def ler_arquivo(arquivo):
    with open(arquivo, "r") as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]

    n, m = map(int, linhas[0].split(";"))

    nos = []
    coordenadas = []
    for i in range(1, n + 1):
        partes = linhas[i].split(";")
        nos.append(partes[0])
        coordenadas.append([float(partes[1]), float(partes[2])])

    matriz = []
    for i in range(n + 1, n + 1 + n):
        matriz.append(list(map(int, linhas[i].split(";"))))

    forcas = []
    for i in range(n + 1 + n, n + 1 + n + n):
        Px, Py = map(float, linhas[i].split(";"))
        forcas.append((Px, Py))

    vinculos = []
    for i in range(n + 1 + n + n, n + 1 + n + n + n):
        vinculos.append(linhas[i])

    return n, m, nos, coordenadas, matriz, forcas, vinculos


# --- Função para processar o arquivo selecionado, usa LER_ARQUIVO() ---
def processar_trelica(caminho_completo):
    
        n, m, nos, coords, matriz, forcas, vinculos = ler_arquivo(caminho_completo)

        ss = SystemElements()
        
        # Elementos
        for i in range(n):                          
            for j in range(i + 1, n):
                if matriz[i][j] == 1:
                    ss.add_truss_element(location=[coords[i], coords[j]])
        
        # Vínculos
        for i, v in enumerate(vinculos):            
            if v == "P":
                ss.add_support_hinged(node_id=i + 1)
            elif v == "X":
                ss.add_support_roll(node_id=i + 1, direction=2)
            elif v == "Y":
                ss.add_support_roll(node_id=i + 1, direction=1)
        
        # Forças
        for i, (Fx, Fy) in enumerate(forcas):       
            if Fx != 0 or Fy != 0:
                ss.point_load(node_id=i + 1, Fx=Fx, Fy=Fy)
        
        ss.solve()
        
        return ss