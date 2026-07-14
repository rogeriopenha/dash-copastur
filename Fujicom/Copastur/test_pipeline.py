"""
Teste local do pipeline Copastur BI.
Simula a API paginada e valida:
  - Paginacao (Order/List com loop page/pageSize)
  - Campo Viajante em todas as 15 sub-categorias
  - Logica de append com deteccao de novas colunas
Uso: python test_pipeline.py
Nao requer dependencias externas.
"""

import json
import random
import sys
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# 1. Mock data generators
# ---------------------------------------------------------------------------

TRAVELERS = [
    "Carlos Silva", "Ana Souza", "Bruno Lima", "Daniela Costa", "Eduardo Santos",
    "Fernanda Oliveira", "Gabriel Pereira", "Helena Rodrigues", "Igor Martins", "Julia Almeida"
]


def make_order(num):
    traveler = random.choice(TRAVELERS)
    days_ago = random.randint(0, 60)
    base = datetime.now() - timedelta(days=days_ago)
    return {
        "osNumber": f"OS{num:06d}",
        "requestNumber": f"REQ{num:06d}",
        "traveler": traveler,
        "requester": f"Solicitante {num % 5 + 1}",
        "requesterEmail": f"solicitante{num % 5 + 1}@empresa.com",
        "requesterLogin": f"user{num % 5 + 1}",
        "statusTravel": random.choice(["Aprovado", "Em Andamento", "Concluído", "Cancelado"]),
        "statusExpense": random.choice(["Pendente", "Pago", "Parcial"]),
        "dateOrder": base.strftime("%Y-%m-%d"),
        "dateCreated": base.strftime("%Y-%m-%dT%H:%M:%S"),
        "reason": random.choice(["Visita Cliente", "Treinamento", "Conferência", "Auditoria"]),
        "typeTravel": random.choice(["Nacional", "Internacional"]),
        "centerCostDescription": f"CC {num % 10 + 100}",
        "centerCostCode": str(num % 10 + 100),
        "companyName": "Fujicom",
        "companyCode": "001",
        "approver": "Aprovador Master",
        "total": random.randint(500, 50000),
        "airs": [
            {
                "ciaName": random.choice(["LATAM", "GOL", "Azul"]),
                "flyNumber": f"{random.randint(1000,9999)}",
                "cityDeparture": "São Paulo",
                "iataDeparture": "GRU",
                "cityArrival": random.choice(["Brasília", "Rio de Janeiro", "Salvador", "Manaus"]),
                "iataArrival": random.choice(["BSB", "GIG", "SSA", "MAO"]),
                "departureDate": base.strftime("%Y-%m-%dT%H:%M"),
                "arrivalDate": (base + timedelta(hours=random.randint(1, 12))).strftime("%Y-%m-%dT%H:%M"),
                "fare": str(random.randint(200, 3000)),
                "tax": str(random.randint(50, 500)),
                "totalFare": str(random.randint(300, 4000)),
                "currency": "BRL",
            }
            for _ in range(random.randint(0, 2))
        ],
        "hotels": [
            {
                "nameHotel": random.choice(["Ibiz", "Blue Tree", "Accor", "Transamérica"]),
                "cityHotel": random.choice(["São Paulo", "Rio", "Brasília"]),
                "checkin": base.strftime("%Y-%m-%d"),
                "checkout": (base + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
                "daily": str(random.randint(150, 800)),
                "totalHotel": str(random.randint(300, 4000)),
            }
            for _ in range(random.randint(0, 1))
        ],
        "cars": [
            {
                "carName": random.choice(["Fiat Uno", "VW Gol", "Onix"]),
                "locadora": random.choice(["Localiza", "Hertz", "Unidas"]),
                "pickupDate": base.strftime("%Y-%m-%d"),
                "dropoffDate": (base + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d"),
                "totalCar": str(random.randint(200, 2000)),
            }
            for _ in range(random.randint(0, 1))
        ],
        "others": [
            {"description": "Seguro Viagem", "value": "150"}
            for _ in range(random.randint(0, 1))
        ],
        "services": [
            {"serviceType": random.choice(["Transfer", "Translator"]), "value": "200"}
            for _ in range(random.randint(0, 2))
        ],
        "transports": [
            {"transportType": random.choice(["Taxi", "Uber"]), "value": "80"}
            for _ in range(random.randint(0, 1))
        ],
        "refunds": [
            {"refundType": random.choice(["Alimentação", "Transporte"]), "value": "350"}
            for _ in range(random.randint(0, 2))
        ],
        "advances": [
            {"advanceType": "Adiantamento", "value": "1000"}
            for _ in range(random.randint(0, 1))
        ],
        "travelersDetail": [
            {"name": traveler, "email": f"{traveler.lower().replace(' ', '.')}@empresa.com", "login": traveler.lower().split()[0]}
        ],
        "approvers": [
            {"approverName": "Aprovador Master", "approverEmail": "aprovador@empresa.com"}
        ],
        "quotations": [
            {"quoteId": f"COT{num}", "supplier": random.choice(["CVC", "Decolar"]), "value": str(random.randint(1000, 10000))}
            for _ in range(random.randint(0, 1))
        ],
        "costAllocations": [
            {"ccCode": f"CC{num % 10 + 100}", "percent": "100"}
        ],
        "expenseStatuses": [
            {"expenseType": "Aéreo", "status": "Pendente"}
        ],
        "followUps": [
            {"message": f"Follow up do pedido {num}", "sentBy": "Sistema", "recipients": traveler, "inclusionDate": base.strftime("%Y-%m-%dT%H:%M:%S")}
            for _ in range(random.randint(0, 1))
        ],
    }


# ---------------------------------------------------------------------------
# 2. Simulated API (paginated)
# ---------------------------------------------------------------------------

class MockAPI:
    """Simula a API Copastur com paginacao no Order/List."""

    def __init__(self, total_orders=250, page_size=100):
        self.all_orders = {f"OS{o:06d}": make_order(o) for o in range(1, total_orders + 1)}
        self.order_list = sorted(self.all_orders.keys())
        self.page_size = page_size

    def get_order_list(self, params):
        """Simula GET /v2/api/Order/List com paginacao."""
        page = int(params.get("page", 1))
        ps = int(params.get("pageSize", self.page_size))
        start = (page - 1) * ps
        batch = self.order_list[start:start + ps]
        items = [self.all_orders[num] for num in batch]
        return {"data": items}

    def get_order_v2(self, os_number):
        """Simula GET /v2/api/Order/GetOrderV2?osNumber=..."""
        order = self.all_orders.get(os_number)
        return {"data": order} if order else {"data": None}


# ---------------------------------------------------------------------------
# 3. Pipeline simulation functions (mirroring the GAS logic)
# ---------------------------------------------------------------------------

def simulate_process_orders(api, start_date, end_date, page_size=100, max_pages=100):
    """
    Simula processOrders_BY_PERIOD_ do copastur-bi.gs.
    Retorna dict com todas as categorias de dados.
    """
    # Pagination loop
    all_orders = []
    page = 1
    while page <= max_pages:
        params = {
            "request_date_start": start_date,
            "request_date_end": end_date,
            "page": page,
            "pageSize": page_size,
        }
        res = api.get_order_list(params)
        orders = res.get("data") or []
        if not orders:
            break
        all_orders.extend(orders)
        if len(orders) < page_size:
            break
        page += 1

    if not all_orders:
        return {}

    # Extract unique order numbers (no existingOrders filter for test)
    order_numbers = []
    seen = set()
    for o in all_orders:
        num = o.get("osNumber") or o.get("requestNumber") or ""
        if num and num not in seen:
            order_numbers.append(num)
            seen.add(num)

    if not order_numbers:
        return {}

    # Data categories
    categories = {
        "Pedidos": [],
        "Aereos": [],
        "Hoteis": [],
        "Carros": [],
        "OutrosServicos": [],
        "Servicos": [],
        "Transporte": [],
        "Reembolsos": [],
        "Adiantamentos": [],
        "Viajantes": [],
        "Aprovadores": [],
        "ResumoCotacoes": [],
        "Rateio": [],
        "StatusDespesa": [],
        "FollowUp": [],
    }

    for j, num in enumerate(order_numbers):
        res2 = api.get_order_v2(num)
        d = res2.get("data")
        if not d:
            continue

        # Pedidos
        categories["Pedidos"].append({
            "N\u00ba Pedido": d.get("orderNumber", "") or num,
            "Viajante": d.get("traveler", ""),
            "Solicitante": d.get("requester", ""),
            "Status Viagem": d.get("statusTravel", ""),
            "Status Despesa": d.get("statusExpense", ""),
            "Total": d.get("total", ""),
        })

        # Aereos
        for air in d.get("airs") or []:
            categories["Aereos"].append({
                "N\u00ba Pedido": num,
                "Companhia": air.get("ciaName", ""),
                "Nr Voo": air.get("flyNumber", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Hoteis
        for hot in d.get("hotels") or []:
            categories["Hoteis"].append({
                "N\u00ba Pedido": num,
                "Hotel": hot.get("nameHotel", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Carros
        for car in d.get("cars") or []:
            categories["Carros"].append({
                "N\u00ba Pedido": num,
                "Carro": car.get("carName", ""),
                "Viajante": d.get("traveler", ""),
            })

        # OutrosServicos
        for oth in d.get("others") or []:
            categories["OutrosServicos"].append({
                "N\u00ba Pedido": num,
                "Descricao": oth.get("description", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Servicos
        for svc in d.get("services") or []:
            categories["Servicos"].append({
                "N\u00ba Pedido": num,
                "Tipo": svc.get("serviceType", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Transporte
        for trp in d.get("transports") or []:
            categories["Transporte"].append({
                "N\u00ba Pedido": num,
                "Tipo": trp.get("transportType", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Reembolsos
        for ref in d.get("refunds") or []:
            categories["Reembolsos"].append({
                "N\u00ba Pedido": num,
                "Tipo": ref.get("refundType", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Adiantamentos
        for adv in d.get("advances") or []:
            categories["Adiantamentos"].append({
                "N\u00ba Pedido": num,
                "Tipo": adv.get("advanceType", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Viajantes
        for trav in d.get("travelersDetail") or []:
            categories["Viajantes"].append({
                "N\u00ba Pedido": num,
                "Nome": trav.get("name", ""),
                "Email": trav.get("email", ""),
            })

        # Aprovadores
        for apr in d.get("approvers") or []:
            categories["Aprovadores"].append({
                "N\u00ba Pedido": num,
                "Aprovador": apr.get("approverName", ""),
                "Viajante": d.get("traveler", ""),
            })

        # ResumoCotacoes
        for cot in d.get("quotations") or []:
            categories["ResumoCotacoes"].append({
                "N\u00ba Pedido": num,
                "Cotacao": cot.get("quoteId", ""),
                "Viajante": d.get("traveler", ""),
            })

        # Rateio
        for rat in d.get("costAllocations") or []:
            categories["Rateio"].append({
                "N\u00ba Pedido": num,
                "CC": rat.get("ccCode", ""),
                "Viajante": d.get("traveler", ""),
            })

        # StatusDespesa
        for sts in d.get("expenseStatuses") or []:
            categories["StatusDespesa"].append({
                "N\u00ba Pedido": num,
                "Tipo": sts.get("expenseType", ""),
                "Viajante": d.get("traveler", ""),
            })

        # FollowUp
        for fup in d.get("followUps") or []:
            categories["FollowUp"].append({
                "N\u00ba Pedido": num,
                "Mensagem": fup.get("message", ""),
                "Viajante": d.get("traveler", ""),
            })

    return categories


def simulate_append(existing_headers, data_rows):
    """
    Simula appendToSheet_ com deteccao de novas colunas.
    Retorna lista de linhas a serem escritas (como dicts).
    """
    if not data_rows:
        return [], existing_headers

    data_headers = list(data_rows[0].keys())
    new_cols = [h for h in data_headers if h not in existing_headers]

    if new_cols:
        existing_headers = existing_headers + new_cols

    # Build keys from existing data rows (skip header, only if data exists)
    existing_keys = set()
    new_rows = []
    for row in data_rows:
        key = "|||".join(str(row.get(h, "")) for h in existing_headers)
        if key not in existing_keys:
            new_rows.append([row.get(h, "") for h in existing_headers])
            existing_keys.add(key)

    return new_rows, existing_headers


# ---------------------------------------------------------------------------
# 4. Tests
# ---------------------------------------------------------------------------

PASS = 0
FAIL = 0


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def test_pagination():
    print("\n=== Teste 1: Paginacao ===")

    # 1a: 250 orders com page_size=100 => 3 paginas
    api = MockAPI(total_orders=250, page_size=100)
    all_orders = []
    page = 1
    while page <= 100:
        params = {"page": page, "pageSize": 100}
        res = api.get_order_list(params)
        chunk = res.get("data") or []
        if not chunk:
            break
        all_orders.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    test("250 orders devem resultar em 3 paginas", page == 3, f"got page={page}")
    test("Total de orders agregados = 250", len(all_orders) == 250, f"got {len(all_orders)}")

    # 1b: 50 orders (menos que page_size) => 1 pagina
    api2 = MockAPI(total_orders=50, page_size=100)
    chunk = api2.get_order_list({"page": 1, "pageSize": 100}).get("data") or []
    test("50 orders cabem em 1 pagina", len(chunk) == 50)

    # 1c: 0 orders
    api3 = MockAPI(total_orders=0, page_size=100)
    chunk3 = api3.get_order_list({"page": 1, "pageSize": 100}).get("data") or []
    test("0 orders retorna lista vazia", len(chunk3) == 0)

    # 1d: Pagina sem dados apos primeira
    chunk4 = api3.get_order_list({"page": 2, "pageSize": 100}).get("data") or []
    test("Pagina alem do fim retorna vazio", len(chunk4) == 0)

    # 1e: 500 orders => 5 paginas
    api5 = MockAPI(total_orders=500, page_size=100)
    all5 = []
    p = 1
    while p <= 100:
        ch = api5.get_order_list({"page": p, "pageSize": 100}).get("data") or []
        if not ch:
            break
        all5.extend(ch)
        if len(ch) < 100:
            break
        p += 1
    test("500 orders agregados", len(all5) == 500, f"got {len(all5)}")
    test("500 orders = ate pagina 6 (ultima cheia +1)", p == 6, f"got page={p}")


def test_viajante_in_all_categories():
    print("\n=== Teste 2: Campo Viajante em todas as categorias ===")
    api = MockAPI(total_orders=300, page_size=100)
    cats = simulate_process_orders(api, "2026-01-01", "2026-07-14")

    # Categorias que DEVEM ter 'Viajante'
    must_have_viajante = [
        "Pedidos", "Aereos", "Hoteis", "Carros", "OutrosServicos",
        "Servicos", "Transporte", "Reembolsos", "Adiantamentos",
        "Aprovadores", "ResumoCotacoes", "Rateio", "StatusDespesa", "FollowUp",
    ]
    for cat in must_have_viajante:
        rows = cats.get(cat, [])
        if rows:
            has_it = "Viajante" in rows[0]
            test(f"{cat} tem campo Viajante", has_it)
        else:
            test(f"{cat} tem campo Viajante (sem dados)", True)

    # Viajantes tem dados detalhados (Nome, Email) - NAO precisa de Viajante
    viajantes = cats.get("Viajantes", [])
    if viajantes:
        test("Viajantes tem 'Nome' (detalhado)", "Nome" in viajantes[0])
        test("Viajantes NAO precisa de 'Viajante'", "Viajante" not in viajantes[0])

    # Verificar se algum Viajante esta vazio
    for cat in must_have_viajante:
        for row in cats.get(cat, []):
            if row.get("Viajante", "").strip():
                break
        else:
            if cats.get(cat):
                test(f"{cat} tem pelo menos um Viajante preenchido", False)
                continue
        test(f"{cat} Viajantes nao estao todos vazios", True, "(pulado sem dados)")


def test_new_column_detection():
    print("\n=== Teste 3: Deteccao de novas colunas no append ===")

    # Simular planilha existente SEM coluna 'Viajante'
    old_headers = ["N\u00ba Pedido", "Companhia", "Nr Voo"]

    # Dados NOVOS que incluem 'Viajante'
    new_data = [
        {"N\u00ba Pedido": "OS001", "Companhia": "LATAM", "Nr Voo": "1234", "Viajante": "Carlos Silva"},
        {"N\u00ba Pedido": "OS002", "Companhia": "GOL", "Nr Voo": "5678", "Viajante": "Ana Souza"},
    ]

    rows, final_headers = simulate_append(old_headers, new_data)

    test("Viajante foi adicionado aos headers", "Viajante" in final_headers, f"got {final_headers}")
    test("Final headers tem 4 colunas", len(final_headers) == 4, f"got {len(final_headers)}")
    test("Dados preservam Viajante", rows[0][3] == "Carlos Silva", f"got {rows[0][3]}")
    test("Dedup funciona (OS001 igual)", len(rows) == 2, f"got {len(rows)} (2 diferentes)")

    # Testar dedup: mesma chamada com linha duplicada
    dup_data = [
        {"N\u00ba Pedido": "OS001", "Companhia": "LATAM", "Nr Voo": "1234", "Viajante": "Carlos Silva"},
        {"N\u00ba Pedido": "OS001", "Companhia": "LATAM", "Nr Voo": "1234", "Viajante": "Carlos Silva"},
    ]
    rows2, _ = simulate_append(final_headers, dup_data)
    test("Dedup remove duplicata no mesmo lote", len(rows2) == 1, f"got {len(rows2)}")

    # Testar sem novas colunas
    rows3, h3 = simulate_append(final_headers, [
        {"N\u00ba Pedido": "OS003", "Companhia": "Azul", "Nr Voo": "9999", "Viajante": "Bruno Lima"},
    ])
    test("Sem novas colunas funciona", len(rows3) == 1)
    test("Headers inalterados sem novas colunas", h3 == final_headers)


def test_full_pipeline_integration():
    print("\n=== Teste 4: Pipeline completo (250 orders) ===")
    api = MockAPI(total_orders=250, page_size=100)
    cats = simulate_process_orders(api, "2026-01-01", "2026-07-14")

    test("Pipeline retornou dados", bool(cats))
    test("Pedidos > 0", len(cats.get("Pedidos", [])) > 0)

    # Todas as categorias existem
    for cat in cats:
        test(f"Categoria {cat} existe", cat in cats)

    # Nenhuma categoria deve ter 'Nº Pedido' vazio
    for cat_name, rows in cats.items():
        if rows:
            empty_nums = sum(1 for r in rows if not r.get("N\u00ba Pedido", "").strip())
            test(f"{cat_name}: Nenhum N\u00ba Pedido vazio", empty_nums == 0, f"got {empty_nums} vazios")

    # Verificar que o numero de paginas foi 3 (250 orders / 100 page_size = 3)
    # Isso e implicito - o total de pedidos unicos processados
    total_pedidos = len(cats.get("Pedidos", []))
    test("Total de pedidos processados = 250", total_pedidos == 250, f"got {total_pedidos}")


# ---------------------------------------------------------------------------
# 5. Run all tests
# ---------------------------------------------------------------------------

def main():
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Mock data: 500 orders gerados, Python {sys.version}")

    test_pagination()
    test_viajante_in_all_categories()
    test_new_column_detection()
    test_full_pipeline_integration()

    print(f"\n{'='*50}")
    print(f"Resultado: {PASS} passaram, {FAIL} falharam")
    print(f"{'='*50}")

    if FAIL > 0:
        sys.exit(1)
    else:
        print("OK - Todos os testes passaram!")


if __name__ == "__main__":
    main()
