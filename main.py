from fastapi import FastAPI, HTTPException

app = FastAPI(title="TechStore API")

# ---------- BASE DE DATOS FALSA (en memoria) ----------
productos = [
    {"id": 1, "nombre": "Laptop Pro", "categoria": "computadoras", "precio": 1200, "stock": 5},
    {"id": 2, "nombre": "Mouse Inalámbrico", "categoria": "accesorios", "precio": 25, "stock": 50},
    {"id": 3, "nombre": "Teclado Mecánico", "categoria": "accesorios", "precio": 80, "stock": 0},
    {"id": 4, "nombre": "Monitor 27\"", "categoria": "computadoras", "precio": 300, "stock": 12},
    {"id": 5, "nombre": "Audífonos BT", "categoria": "audio", "precio": 60, "stock": 30},
    {"id": 6, "nombre": "Parlante Mini", "categoria": "audio", "precio": 45, "stock": 8},
    {"id": 7, "nombre": "Tablet 10\"", "categoria": "computadoras", "precio": 250, "stock": 15}
]


pedidos = [
    {"id": 101, "cliente_id": 1, "producto": "Laptop Pro", "total": 1200, "estado": "completado"},
    {"id": 102, "cliente_id": 1, "producto": "Mouse Inalámbrico", "total": 25, "estado": "pendiente"},
    {"id": 103, "cliente_id": 1, "producto": "Monitor 27\"", "total": 300, "estado": "completado"},
    {"id": 104, "cliente_id": 2, "producto": "Audífonos BT", "total": 60, "estado": "pendiente"},
    {"id": 105, "cliente_id": 2, "producto": "Tablet 10\"", "total": 250, "estado": "completado"},
]


# ---------- ENDPOINT DE BIENVENIDA ----------
@app.get("/")
async def inicio():
    return {"mensaje": "Bienvenido a TechStore 🛒", "total_productos": len(productos)}

# ---------- PATH PARAMETER: un producto específico ----------
@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: int):
    # LÓGICA REAL: buscar en la lista el producto con ese ID
    for producto in productos:
        if producto["id"] == producto_id:
            return producto

    # Si llegamos aquí, el producto NO existe -> error 404
    raise HTTPException(
        status_code=404,
        detail=f"El producto con id {producto_id} no existe 🤷"
    )

# ---------- QUERY PARAMETERS: listar con filtros ----------
@app.get("/productos")
async def listar_productos(
    categoria: str | None = None,
    max_precio: float | None = None,
    solo_disponibles: bool = False,
    orden: str = "id",
    pagina: int = 1,
    tamano: int = 3
):
    resultado = productos.copy()

    # FILTRO 1: por categoría
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]

    # FILTRO 2: por precio máximo
    if max_precio is not None:
        resultado = [p for p in resultado if p["precio"] <= max_precio]

    # FILTRO 3: solo los que tienen stock
    if solo_disponibles:
        resultado = [p for p in resultado if p["stock"] > 0]

    # ORDENAMIENTO
    if orden == "precio_asc":
        resultado.sort(key=lambda p: p["precio"])
    elif orden == "precio_desc":
        resultado.sort(key=lambda p: p["precio"], reverse=True)

    # PAGINACIÓN
    inicio = (pagina - 1) * tamano
    fin = inicio + tamano
    pagina_resultados = resultado[inicio:fin]

    return {
        "total_encontrados": len(resultado),
        "pagina": pagina,
        "tamano": tamano,
        "productos": pagina_resultados
    }

# ---------- PATH + QUERY COMBINADOS ----------
@app.get("/clientes/{cliente_id}/pedidos")
async def pedidos_del_cliente(
    cliente_id: int,
    estado: str | None = None,
    orden: str = "id"
):
    # LÓGICA: tomar solo los pedidos de ESTE cliente
    mis_pedidos = [p for p in pedidos if p["cliente_id"] == cliente_id]

    if not mis_pedidos:
        raise HTTPException(
            status_code=404,
            detail=f"El cliente {cliente_id} no tiene pedidos 🤷"
        )

    # Filtro opcional por estado
    if estado:
        mis_pedidos = [p for p in mis_pedidos if p["estado"] == estado]

    # Orden opcional por total
    if orden == "total_desc":
        mis_pedidos.sort(key=lambda p: p["total"], reverse=True)

    # Calcular el gasto total del cliente
    gasto_total = sum(p["total"] for p in mis_pedidos)

    return {
        "cliente_id": cliente_id,
        "cantidad_pedidos": len(mis_pedidos),
        "gasto_total": gasto_total,
        "pedidos": mis_pedidos
    }

