def generate_diagnosis(cpu, ram, disk):

    problems = []

    # CPU
    if cpu > 85:
        problems.append("CPU em uso crítico (possível travamento)")
    elif cpu > 60:
        problems.append("CPU em uso elevado")
    else:
        problems.append("CPU em nível estável")

    # RAM
    if ram > 85:
        problems.append("RAM crítica (quase cheia)")
    elif ram > 70:
        problems.append("RAM em uso moderado-alto")
    else:
        problems.append("RAM estável")

    # DISCO
    if disk > 90:
        problems.append("Disco quase cheio (risco alto de travamentos)")
    elif disk > 80:
        problems.append("Disco com pouco espaço livre")
    else:
        problems.append("Disco saudável")

    return " | ".join(problems)
