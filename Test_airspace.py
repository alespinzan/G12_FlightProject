from airspace import AirSpace

# Crear instancia
asp = AirSpace()

# Cargar datos
asp.load_navpoints("Cat_nav.txt")
asp.load_navsegments("Cat_seg.txt")
asp.load_airports("Cat_aer.txt")

# Imprimir nodos (NavPoints)
print("NavPoints cargados:")
for np in asp.navpoints.values():
    print(f"  {np.id}: {np.name} ({np.latitude}, {np.longitude})")

# Imprimir aeropuertos
print("\nAeropuertos cargados:")
for ap in asp.airports.values():
    print(f"  {ap.id}: SIDs={ap.sids}, STARs={ap.stars}")

# Imprimir segmentos
print("\nNavSegments cargados:")
for seg in asp.navsegments:
    print(f"  {seg.id}: {seg.origin.id} -> {seg.destination.id} (dist={seg.distance:.2f})")