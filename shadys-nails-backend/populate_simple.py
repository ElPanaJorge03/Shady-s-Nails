"""
Script simplificado para poblar la base de datos de producción
"""

import psycopg2

DATABASE_URL = "postgresql://admin:eRiwtbZz95m6LzHyV0Fp2573fBqty6d5@dpg-d52cjie3jp1c73c0qtj0-a.oregon-postgres.render.com/shadys_nails_prod"

print("🔌 Conectando...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True  # Auto-commit cada operación
cursor = conn.cursor()

print("✅ Conectado!\n")

try:
    # Workers
    print("👷 Creando worker...")
    cursor.execute("""
        INSERT INTO workers (name, phone, email, business_name, state, password_hash, role)
        VALUES ('Gina Paola Martinez Barrera', '3003710184', 'gina.paola@shadysnails.com', 'Shady''s Nails', true, 
                '$2b$12$yKQc8kq9S0sKr6gpHXGiLefxDxkRGmya84MR4h5K544Di6XqyRZLi', 'admin')
        ON CONFLICT (email) DO NOTHING
        RETURNING id;
    """)
    result = cursor.fetchone()
    if result:
        worker_id = result[0]
        print(f"   ✅ Worker creado con ID: {worker_id}")
    else:
        cursor.execute("SELECT id FROM workers WHERE email = 'gina.paola@shadysnails.com'")
        worker_id = cursor.fetchone()[0]
        print(f"   ℹ️  Worker ya existe con ID: {worker_id}")
    
    # Services
    print("\n💅 Creando servicios...")
    services = [
        ('Manicure Tradicional', 60, 25000),
        ('Manicure Semipermanente', 90, 35000),
        ('Manicure Gel', 120, 45000),
        ('Acrílicas', 120, 50000),
        ('Pedicure Tradicional', 60, 30000),
        ('Pedicure Spa', 90, 40000),
        ('Esmaltado Permanente', 45, 20000),
        ('Retiro de Uñas', 30, 15000)
    ]
    
    for name, duration, price in services:
        cursor.execute(f"""
            INSERT INTO services (worker_id, name, duration_minutes, price, state)
            VALUES ({worker_id}, '{name}', {duration}, {price}, true)
            ON CONFLICT DO NOTHING;
        """)
        print(f"   ✅ {name}")
    
    # Additionals
    print("\n✨ Creando adicionales...")
    additionals = [
        ('Diseños Simples', 15, 3000),
        ('Diseños Complejos', 30, 5000),
        ('Diseños Premium', 45, 8000),
        ('Piedras y Accesorios', 20, 4000),
        ('French', 10, 2000)
    ]
    
    for name, duration, price in additionals:
        cursor.execute(f"""
            INSERT INTO additionals (name, extra_duration, price, state)
            VALUES ('{name}', {duration}, {price}, true);
        """)
        print(f"   ✅ {name}")
    
    # Customers
    print("\n👥 Creando clientes...")
    customers = [
        ('Ana García', '3001234567', 'ana.garcia@example.com'),
        ('María López', '3009876543', 'maria.lopez@example.com'),
        ('Laura Martínez', '3005551234', 'laura.martinez@example.com'),
        ('Carolina Rodríguez', '3007778888', 'carolina.rodriguez@example.com'),
        ('Valentina Sánchez', '3002223333', 'valentina.sanchez@example.com')
    ]
    
    for name, phone, email in customers:
        cursor.execute(f"""
            INSERT INTO customers (name, phone, email)
            VALUES ('{name}', '{phone}', '{email}')
            ON CONFLICT (email) DO NOTHING;
        """)
        print(f"   ✅ {name}")
    
    # Users
    print("\n🔐 Creando usuario admin...")
    cursor.execute("""
        INSERT INTO users (email, password_hash, name, phone, role)
        SELECT email, password_hash, name, phone, 'worker'
        FROM workers
        WHERE email = 'gina.paola@shadysnails.com'
        ON CONFLICT (email) DO NOTHING;
    """)
    print("   ✅ Usuario admin creado")
    
    # Verificación
    print("\n" + "="*60)
    print("📊 VERIFICACIÓN")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM workers")
    print(f"✅ Workers: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM services")
    print(f"✅ Services: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM additionals")
    print(f"✅ Additionals: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"✅ Customers: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"✅ Users: {cursor.fetchone()[0]}")
    
    print("\n🎉 ¡BASE DE DATOS POBLADA EXITOSAMENTE!")
    print("\n🔐 Credenciales:")
    print("   Email: gina.paola@shadysnails.com")
    print("   Password: shadysnails2024")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
    print("\n✅ Conexión cerrada")
