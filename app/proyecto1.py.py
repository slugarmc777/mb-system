from datetime import datetime

class Pago:
    """Representa un pago realizado por un estudiante."""
    def __init__(self, id_pago: str, estudiante_id: str, monto: float, referencia: str):
        self.id_pago = id_pago
        self.estudiante_id = estudiante_id
        self.monto = monto
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.referencia = referencia

class GestionFinanciera:
    """Gestiona la situación financiera y el registro de pagos de la universidad."""
    def __init__(self):
        # Simulación de base de datos de deudas iniciales por estudiante
        self.deudas_estudiantes = {
            "2026101": 500.00,
            "2026102": 0.00,
            "2026103": 1200.50
        }
        self.historial_pagos = []

    def consultar_estado(self, estudiante_id: str) -> dict:
        """Consulta la situación financiera actual del estudiante (KISS)."""
        if estudiante_id not in self.deudas_estudiantes:
            return {"error": "Estudiante no encontrado en el sistema financiero."}
        
        deuda = self.deudas_estudiantes[estudiante_id]
        estado = "Paz y Salvo" if deuda <= 0 else "Deudor"
        
        return {
            "estudiante_id": estudiante_id,
            "saldo_pendiente": deuda,
            "estado_financiero": estado
        }

    def registrar_pago(self, id_pago: str, estudiante_id: str, monto: float, referencia: str) -> dict:
        """Registra un pago y actualiza la deuda del estudiante (DRY & Modular)."""
        if estudiante_id not in self.deudas_estudiantes:
            return {"exito": False, "mensaje": "Estudiante no registrado."}
        
        if monto <= 0:
            return {"exito": False, "mensaje": "El monto del pago debe ser mayor a cero."}

        # Registrar el pago
        nuevo_pago = Pago(id_pago, estudiante_id, monto, referencia)
        self.historial_pagos.append(nuevo_pago)

        # Actualizar la deuda
        self.deudas_estudiantes[estudiante_id] -= monto
        if self.deudas_estudiantes[estudiante_id] < 0:
            self.deudas_estudiantes[estudiante_id] = 0.0  # Evita saldos negativos

        return {
            "exito": True,
            "mensaje": "Pago registrado exitosamente.",
            "nuevo_saldo": self.deudas_estudiantes[estudiante_id]
        }

# --- Bloque de prueba local ---
if __name__ == "__main__":
    finanzas = GestionFinanciera()
    
    # 1. Consultar estado inicial
    print("--- Estado Inicial ---")
    print(finanzas.consultar_estado("2026101"))
    
    # 2. Registrar un pago
    print("\n--- Registrando Pago ---")
    print(finanzas.registrar_pago("P001", "2026101", 200.00, "REF12345"))
    
    # 3. Consultar estado actualizado
    print("\n--- Estado Actualizado ---")
    print(finanzas.consultar_estado("2026101"))

    

    