def diagnose_patch(self, ram, disk, freq):
    msg = []

    # ================= RAM =================
    if ram["percent"] < 60:
        msg.append("🟢 RAM baixa, sistema fluido.")
    elif ram["percent"] < 85:
        msg.append("🟡 RAM moderada, muitos processos em execução.")
    else:
        msg.append("🔴 RAM alta, risco de lentidão.")

    # ================= DISK =================
    if disk["percent"] < 70:
        msg.append("🟢 Disco OK.")
    elif disk["percent"] < 90:
        msg.append("🟡 Disco moderado.")
    else:
        msg.append("🔴 Disco cheio.")

    # ================= CPU (RESTAURADO + MELHORADO) =================
    if freq:
        load = (freq.current / freq.max) * 100 if freq.max else 0

        if load < 50:
            msg.append("🟢 CPU com baixo uso, sistema leve e sem carga.")
        elif load < 80:
            msg.append("🟡 CPU em uso moderado, há processos ativos em execução.")
        else:
            msg.append("🔴 CPU em alta carga, possível lentidão no sistema.")

    return "\n".join(msg)
