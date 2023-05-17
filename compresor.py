import time
import sys
###############################################################################################
##                                    Compresor Mágico                                       ##
###############################################################################################
start_time = time.time()

# Se crea una lista de caracteres que va a tener cada linea del archivo a comprimir (Lines),
# luego usamos otra lista para guardar cada letra (my_string)
Lines = []
for line in open(sys.argv[1], 'rb').readlines():
  Lines.append(line)
my_string=[]
for h in Lines:
  for t in h:
    my_string.append(t)
len_my_string = len(my_string)
# Crea una lista de caracteres y la frecuencia de aparicion de cada uno
letters = []
only_letters = []
dic = {}
# Ciclo calcula la frecuencia con la que se repite un caracter
for letter in my_string:
  if letter not in only_letters:
    dic[letter] = 1
    only_letters.append(letter)
  else:
    dic[letter] +=1
for clave in dic:
  letters.append([dic[clave],clave])
nodes = []

for l in letters:
    ayu = []
    nodes.append([int(l[0]),str(l[1])])
    
# Genera la base de level para la frecuencia del arbol de Huffman
nodes.sort()
huffman_tree = []

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
def unir_letras(arr_letras, diccionario):
    # Obtenemos una lista de los valores asociados a cada letra
    valores = list(map(diccionario.get, arr_letras))
    # Filtramos los valores que sean None (no tienen valor asociado)
    valores = filter(lambda v: v is not None, valores)
    # Unimos todos los valores en una única variable en bytes y la devolvemos
    return ''.join(valores)

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
# Crea una secuencia de bits con los códigos nuevos
#bitstring =unir_letras(my_string, letter_binary)
bitstring = ""
bits = []
packsize = 40000
for h in my_string:
  bitstring = bitstring+letter_binary[h]
  if (len(bitstring) > packsize):
    bits.append(bitstring)
    bitstring = ""
bits.append(bitstring)
bitstring = "".join(bits)
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
print(tiempo_ejecucion_r)