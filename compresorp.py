import time
import sys
from mpi4py import MPI
###############################################################################################
##                                    Compresor Mágico                                       ##
###############################################################################################
start_time = time.time()
comm = MPI.COMM_WORLD  # Comunicador entre procesos
rank = comm.Get_rank()  # Identificador del proceso actual
size = comm.Get_size() # Número total de procesos
# Se crea una lista de caracteres que va a tener cada linea del archivo a comprimir (Lines),
# luego usamos otra lista para guardar cada letra (my_string)
def binario_a_bytes(cadena_binaria):
    # Convertimos la cadena binaria a un número entero
    entero = int(cadena_binaria, 2)
    # Convertimos el entero a una variable en bytes utilizando  la longitud mínima de 1 byte
    variable_bytes = entero.to_bytes((entero.bit_length() + 7) // 8, byteorder='big')
    return variable_bytes
def sustituir_valores(arreglo, diccionario):
  # Crea una función lambda que devuelve el valor correspondiente del diccionario para una clave dada
  f = lambda x: diccionario[x] if x in diccionario else x

  # Aplica la función lambda al arreglo utilizando la función vectorizada map()
  resultado_lista = list(map(f, arreglo))

  # Retorna un string con todos los elementos del arreglo unidos
  return b"".join(resultado_lista)
def combine(nodes):

  htree = []
  while len(nodes)>1:
    pos = 0
    newnode = []
    nodes.sort()
    # Agrega el 1 o el 0 dependiendo si sube o baja de nivel
    nodes[pos].append("0")
    nodes[pos+1].append("1")
    huffman_tree.append(nodes[pos])
    huffman_tree.append(nodes[pos+1])
    combined_node1 = nodes[pos][0]+nodes[pos+1][0]
    combined_node2 = ("@"+nodes[pos][1]+"@"+nodes[pos+1][1]+"@")
    newnode.append(combined_node1)
    newnode.append(combined_node2)
    newnodes = []
    newnodes.append(newnode)
    newnodes = newnodes + nodes[2:]
    nodes = newnodes
  huffman_tree.append(nodes[0])
  return huffman_tree

#función que unifica diccionarios
def unificar_diccionarios(diccionarios):

    resultado = {}  # Diccionario resultante
    
    # Iterar sobre cada diccionario en la lista
    for diccionario in diccionarios:
        # Iterar sobre cada letra y su aparición en el diccionario actual
        for letra, aparicion in diccionario.items():
            if letra in resultado:
                resultado[letra] += aparicion  # Sumar apariciones de letra existente
            else:
                resultado[letra] = aparicion  # Agregar nueva letra al diccionario
    
    return resultado

if rank ==0:
  
  Lines = []
  for line in open(sys.argv[1], 'rb').readlines():
    Lines.append(line)
  my_string=[]
  for h in Lines:
    for t in h:
      my_string.append(t)
  len_my_string = len(my_string)
  # Crea una lista de caracteres y la frecuencia de aparicion de cada uno

  for h in range(size):
    cadena_leer = my_string[h*len(my_string)//size:(h+1)*len(my_string)//size ]
    if h!=0:
       comm.send([cadena_leer],dest=h)
    else:
       trozo_leer = cadena_leer

if rank != 0:
  trozo_leer = comm.recv(source=0)[0]

# Ciclo calcula la frecuencia con la que se repite un caracter en cada proceso por separado

only_letters_temp = []
dic_temp = {}
for letter in trozo_leer:
  if letter not in only_letters_temp:
    dic_temp[letter] = 1
    only_letters_temp.append(letter)
  else:
    dic_temp[letter] +=1

if (rank!=0):
   comm.send([only_letters_temp,dic_temp],dest=0)
else: 
  letters = []
  only_letters = []
  aux_dic = []
  dic = {}
  for h in range(size):
    if (h!=0):
      auxx = comm.recv(source=h)
      for ii in auxx[0]:
        if ii not in only_letters:
          only_letters.append(ii)
      aux_dic.append(auxx[1])
    else:
      for ii in only_letters_temp:
        if ii not in only_letters:
          only_letters.append(ii)
      aux_dic.append(dic_temp)

  dic = unificar_diccionarios(aux_dic)
  for clave in dic:
    letters.append([dic[clave],clave])
  nodes = []
  for l in letters:
      ayu = []
      nodes.append([int(l[0]),str(l[1])])  
  # Genera la base de level para la frecuencia del arbol de Huffman
  nodes.sort()
  huffman_tree = []
  newnodes = combine(nodes)
  # Hace que el arbol empiece descendentemente
  huffman_tree.sort(reverse=True)
  checklist = huffman_tree
  # Construye un código binario para cada caracter
  letter_binary = {}
  if len(only_letters) == 1:
    letter_code = [only_letters[0], b"0"]
    letter_binary.append(letter_code*len(my_string))
  else:
    cont = 1
    for letter in only_letters:
      cont+=1
      lettercode = ""
      for node in checklist:
        if len(node) > 2 and ("@"+str(letter)+"@" in node[1] or node[1] == str(letter)):
          lettercode = lettercode + node[2]
      letter_binary[letter]=lettercode
  # Letras con el código binario
  arbol = b""
  for lette in letter_binary:
    arbol = arbol+lette.to_bytes((lette.bit_length() + 7) // 8, byteorder='big')+b"%@%"+letter_binary[lette].encode()+b"%@%"
  # Crea una secuencia de bits con los códigos nuevos.
  #divicion de la cadena completa, enviandola en los diferentes nodos de trabajo.
  for h in range(size):
    cadena_nodo = my_string[h*len(my_string)//size:(h+1)*len(my_string)//size ]
    if h!=0:
       comm.send([cadena_nodo,letter_binary],dest=h)
    else:
       mstring = cadena_nodo

if (rank !=0):
   recibido = comm.recv(source=0)
   mstring = recibido[0]
   letter_binary = recibido[1]
bitstring = ""
bits = []
packsize = 40000

for h in mstring:
  bitstring = bitstring+letter_binary[h]
  if (len(bitstring) > packsize//size):
    bits.append(bitstring)
    bitstring = ""
bits.append(bitstring)
bitstring = "".join(bits)
if (rank!=0):
   comm.send(bitstring,dest=0)
else:
  for h in range(size):
    if (h!=0):    
      aux = comm.recv(source=h)
      bitstring = bitstring+aux
  id = ""
  for i in range(8):
    if bitstring[0]=="0":
      id=id+"0"
      bitstring = bitstring[1:]
    else:
      break 
  bitstring = binario_a_bytes(bitstring)
  # Generar archivo comprimido
  with open("comprimido.elmejorprofesor", "wb") as f:
      f.write(arbol+id.encode()+b"%@%"+bitstring)
  # Indicadores
  end_time = time.time()
  tiempo_ejecucion = end_time - start_time
  tiempo_ejecucion_r = round(tiempo_ejecucion, 2)
  print("El tiempo de ejecución fue:",tiempo_ejecucion_r,"segundos")