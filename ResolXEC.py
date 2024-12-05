import math

# --- Constantes ---
GRAVEDAD = 9.81  # m/s²
CONSTANTE_VICKERS = 1.854

# --- Conversión de unidades ---
def convertir_unidades(valor, unidad_origen, unidad_destino):
    conversiones = {
        ("kg", "kp"): 1, ("kp", "kg"): 1,
        ("cm", "mm"): 10, ("mm", "cm"): 0.1,
        ("g", "kg"): 0.001, ("kg", "g"): 1000,
        ("m", "cm"): 100, ("cm", "m"): 0.01,
        ("mm²", "cm²"): 0.01, ("cm²", "mm²"): 100,
        ("N", "kp"): 0.10197, ("kp", "N"): 9.80665,
        ("m²", "cm²"): 10000, ("cm²", "m²"): 0.0001,
    }
    if (unidad_origen, unidad_destino) in conversiones:
        return valor * conversiones[(unidad_origen, unidad_destino)]
    elif unidad_origen == unidad_destino:
        return valor
    else:
        raise ValueError(f"No se puede convertir de {unidad_origen} a {unidad_destino}")

# --- Funciones de cálculo ---
def calcular_HB(F, S):
    return F / S

def calcular_f(D, d):
    if D**2 < d**2:
        raise ValueError("D² debe ser mayor o igual a d² para calcular f.")
    return 0.5 * (D - math.sqrt(D**2 - d**2))

def calcular_S_brinnel(D, f):
    return math.pi * D * f

def calcular_dureza_vickers(F, d):
    return CONSTANTE_VICKERS * F / (d**2)

def trabajo(m, h0, h1, g=GRAVEDAD):
    return m * g * (h0 - h1)

def trabajo_p(p, S): # Trabajo en función de la resiliencia
    return (p * S)

def resiliencia(W, S):
    return W / S

def esfuerzo_unitario(F, S):
    return F / S

def modulo_young(F, L0, δ, S):
    return (F * L0) / (δ * S)

def alturafinal(h0, W, m, g=GRAVEDAD):

    return (h0 - (W / (m * g)))

# --- Identificación de ensayos ---
def identificar_ensayo(datos):
    if "D" in datos and "d" in datos:
        return "Brinell"
    elif "d" in datos and "t" in datos:
        return "Vickers"
    elif "m" in datos and "h0" in datos and "h1" in datos:
        return "Péndulo de Charpy"
    elif "L0" in datos and "L1" in datos:
        return "Módulo de Young"
    return "Desconocido"

# --- Determinar ensayo con explicación ---
def determinar_ensayo(datos):
    if "D" in datos and "d" in datos and "F" in datos:
        return "Brinell", "Es un ensayo de Brinell porque nos da el D (diámetro de la esfera) y nos especifica que es un penetrador esférico."
    elif "d" in datos and "F" in datos and "HV" in datos:
        return "Vickers", "Es un ensayo de Vickers porque nos da el d (la diagonal de la pirámide) y nos especifica que es un penetrador piramidal."
    elif "m" in datos and "h0" in datos and "h1" in datos:
        return "Péndulo de Charpy", "Es un ensayo con Péndulo de Charpy porque nos dice sobre la masa del martillo, habla de la altura, de un péndulo y la resiliencia."
    elif "S" in datos and "L0" in datos and "L1" in datos:
        return "Módulo de Young", "Es un ensayo de tracción o Módulo de Young porque evalúa deformaciones y fuerzas características de este ensayo."
    else:
        return "Desconocido", "Ensayo desconocido o no se puede calcular con los datos dados."

# --- Generar expresión según la norma ---
def generar_expresion_norma(tipo_ensayo, valores):
    if tipo_ensayo == "Brinell":
        HB = valores.get("HB", {}).get("valor", "X")
        D = valores.get("D", {}).get("valor", "X")
        F = valores.get("F", {}).get("valor", "X")
        t = valores.get("t", {}).get("valor", "X")
        if t != "X":  # Solo incluye 't' si está presente
            return f"{HB} HB {D} / {F} / {t}"
        else:
            return f"{HB} HB {D} / {F}"
    elif tipo_ensayo == "Vickers":
        HV = valores.get("HV", {}).get("valor", "X")
        F = valores.get("F", {}).get("valor", "X")
        t = valores.get("t", {}).get("valor", "X")
        if t != "X":  # Solo incluye 't' si está presente
            return f"{HV} HV {F} / {t}"
        else:
            return f"{HV} HV {F}"
    else:
        return "No aplicable"

# --- Verificar si el valor es númerico ---
def es_numero(valor):
    """Devuelve True si el valor es un número válido (float o int)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


# --- Procesamiento de ejercicios ---
def procesar_ejercicio(nombre, datos):
    ensayo, explicacion = determinar_ensayo(datos)
    resultados = []
    expresion_norma = "No aplicable"

    try:
        if ensayo == "Brinell":
            if "F" in datos and "D" in datos and "d" in datos:
                F = datos["F"]["valor"]
                D = datos["D"]["valor"]
                d = datos["d"]["valor"]
                f = calcular_f(D, d)
                S = calcular_S_brinnel(D, f)
                HB = calcular_HB(F, S)
                datos["HB"] = {"valor": HB, "unidad": "kp/mm²"}
                resultados = [f"f = {f} mm", f"S = {S} mm²", f"HB = {HB} kp/mm²"]
                if "ExpNorma" in datos:
                    expresion_norma = generar_expresion_norma(ensayo, datos)
            else:
                resultados = ["Datos insuficientes para calcular el ensayo de Brinell."]
        
        elif ensayo == "Vickers":
            if "F" in datos and "d" in datos:
                F = datos["F"]["valor"]
                d = datos["d"]["valor"]
                HV = calcular_dureza_vickers(F, d)
                datos["HV"] = {"valor": HV, "unidad": "kp/mm²"}
                resultados = [f"HV = {HV} kp/mm²"]
                if "ExpNorma" in datos:
                    expresion_norma = generar_expresion_norma(ensayo, datos)
            else:
                resultados = ["Datos insuficientes para calcular el ensayo de Vickers."]
        
        elif ensayo == "Péndulo de Charpy":
            if "m" in datos and "h0" in datos and "h1" in datos and "S" in datos:
                m = datos["m"]["valor"]
                h0 = datos["h0"]["valor"]
                h1 = datos["h1"]["valor"]
                S = datos["S"]["valor"]
                W = trabajo(m, h0, h1)
                p = resiliencia(W, S)
                resultados = [f"W = {W} J", f"p = {p} J/cm²"]
            elif "m" in datos and "h0" in datos and "p" in datos and "S" in datos:
                m = datos["m"]["valor"]
                h0 = datos["h0"]["valor"]
                p = datos["p"]["valor"]
                S = datos["S"]["valor"]
                8
                W = trabajo_p(p, S)
                h1 = alturafinal(m, h0, h0)
                resultados = [f"W = {W} J", f"h1 = {h1} m"]

            else:
                resultados = ["Datos insuficientes para calcular el ensayo de Charpy."]
        
        elif ensayo == "Módulo de Young":
            if "L0" in datos and "L1" in datos and "S" in datos and "F" in datos:
                L0 = datos["L0"]["valor"]
                L1 = datos["L1"]["valor"]
                S = datos["S"]["valor"]
                F = datos["F"]["valor"]
                δ = L1 - L0
                σ = esfuerzo_unitario(F, S)
                E = modulo_young(F, L0, δ, S)
                resultados = [f"δ = {δ} mm", f"σ = {σ} N/mm²", f"E = {E} N/mm²"]
            else:
                resultados = ["Datos insuficientes para calcular el Módulo de Young."]
        
        else:
            resultados = ["Ensayo desconocido o no se puede calcular con los datos dados."]
        
        # Generar expresión norma solo si está especificado en los datos
        if "ExpNorma" in datos and datos["ExpNorma"].get("valor") == "X":
            expresion_norma = generar_expresion_norma(ensayo, datos)

    except Exception as e:
        resultados = [f"Error en el cálculo: {e}"]
        expresion_norma = "No aplicable"

    # Solo incluir explicación detallada si el ensayo no se puede identificar
    incluir_explicacion = ensayo == "Desconocido"

    return {
        "nombre": nombre,
        "ensayo": ensayo,
        "explicacion": explicacion if incluir_explicacion else "",
        "resultados": resultados,
        "expresion_norma": expresion_norma
    }

# --- Lectura del archivo ---
def leer_ejercicios_desde_txt(nombre_archivo):
    ejercicios = []
    with open(nombre_archivo, "r") as archivo:
        contenido = archivo.read().split("-DATOS-")[1].strip()
        for bloque in contenido.split("Ejercicio")[1:]:
            lineas = bloque.strip().split("\n")
            nombre = f"Ejercicio {lineas[0]}"
            datos = {}
            for linea in lineas[1:]:
                if "=" in linea:
                    key, value = map(str.strip, linea.split("="))
                    partes = value.split()  # Divide por espacios múltiples
                    if len(partes) == 2:  # Si tiene un valor y una unidad
                        valor, unidad = partes
                        try:
                            valor = float(valor) if valor != "X" else "X"
                        except ValueError:
                            valor = valor  # Mantener el valor como está si no es numérico
                        datos[key] = {"valor": valor, "unidad": unidad}
                    elif len(partes) == 1:  # Si solo tiene un valor
                        valor = partes[0]
                        try:
                            valor = float(valor) if valor != "X" else "X"
                        except ValueError:
                            valor = valor  # Mantener el valor como está si no es numérico
                        datos[key] = {"valor": valor, "unidad": None}
                    else:
                        # Manejo de errores en caso de valores inesperados
                        print(f"Advertencia: Línea no válida '{linea}' en {nombre}")
            ejercicios.append((nombre, datos))
    return ejercicios

# --- Escritura de resultados ---
def guardar_resultados_en_txt(nombre_archivo, resultados):
    with open(nombre_archivo, "w") as archivo:
        for resultado in resultados:
            archivo.write(f"Ejercicio {resultado['nombre']} - Ensayo: {resultado['ensayo']}\n")
            
            # Solo escribe la explicación si es requerida
            if "explicacion" in resultado and resultado["explicacion"]:
                archivo.write(f"Explicación: {resultado['explicacion']}\n")
            
            # Escribe los resultados
            if "resultados" in resultado:
                for res in resultado["resultados"]:
                    archivo.write(f"{res}\n")
            
            # Solo escribe 'ExpNorma' si tiene un valor válido
            if "expresion_norma" in resultado and resultado["expresion_norma"] not in ["No aplicable", None]:
                archivo.write(f"\nExpNorma: {resultado['expresion_norma']}\n")
            
            archivo.write("\n")  # Salto de línea entre ejercicios



# --- Programa principal ---
nombre_archivo_entrada = "/home/silver/Documentos/Programación/XEC/DatosXEC.txt"
nombre_archivo_salida = "resultados.txt"

ejercicios = leer_ejercicios_desde_txt(nombre_archivo_entrada)
resultados = [procesar_ejercicio(nombre, datos) for nombre, datos in ejercicios]
guardar_resultados_en_txt(nombre_archivo_salida, resultados)
print(f"Resultados guardados en {nombre_archivo_salida}")
