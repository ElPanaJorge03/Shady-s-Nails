"""
Script para poblar la base de datos de producción en Render
Ejecuta el seed data de forma automática
"""

import psycopg2

# URL de la base de datos de Render (External Database URL)
DATABASE_URL = "postgresql://admin:eRiwtbZz95m6LzHyV0Fp2573fBqty6d5@dpg-d52cjie3jp1c73c0qtj0-a.oregon-postgres.render.com/shadys_nails_prod"

print("🔌 Conectando a la base de datos de Render...")

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa!")
    print("\n📊 Poblando base de datos...\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 1️⃣ WORKERS
    # ═══════════════════════════════════════════════════════════════
    print("👷 Creando workers...")
    cursor.execute("""
        INSERT INTO workers (name, phone, email, business_name, state, password_hash, role)
        VALUES 
            ('Gina Paola Martinez Barrera', '3003710184', 'gina.paola@shadysnails.com', 'Shady''s Nails', true, 
             '$2b$12$yKQc8kq9S0sKr6gpHXGiLefxDxkRGmya84MR4h5K544Di6XqyRZLi', 'admin')
        ON CONFLICT (email) DO NOTHING;
    """)
    
    # Obtener el ID del worker
    cursor.execute("SELECT id FROM workers WHERE email = 'gina.paola@shadysnails.com'")
    worker_id = cursor.fetchone()[0]
    print(f"   Worker ID: {worker_id}")
    
    # ═══════════════════════════════════════════════════════════════
    # 2️⃣ SERVICES
    # ═══════════════════════════════════════════════════════════════
    print("💅 Creando servicios...")
    cursor.execute(f"""
        INSERT INTO services (worker_id, name, duration_minutes, price, state)
        VALUES 
            ({worker_id}, 'Manicure Tradicional', 60, 25000, true),
            ({worker_id}, 'Manicure Semipermanente', 90, 35000, true),
            ({worker_id}, 'Manicure Gel', 120, 45000, true),
            ({worker_id}, 'Acrílicas', 120, 50000, true),
            ({worker_id}, 'Pedicure Tradicional', 60, 30000, true),
            ({worker_id}, 'Pedicure Spa', 90, 40000, true),
            ({worker_id}, 'Esmaltado Permanente', 45, 20000, true),
            ({worker_id}, 'Retiro de Uñas', 30, 15000, true)
        ON CONFLICT DO NOTHING;
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # 3️⃣ ADDITIONALS
    # ═══════════════════════════════════════════════════════════════
    print("✨ Creando adicionales...")
    cursor.execute("""
        INSERT INTO additionals (name, extra_duration, price, state)
        VALUES 
            ('Diseños Simples', 15, 3000, true),
            ('Diseños Complejos', 30, 5000, true),
            ('Diseños Premium', 45, 8000, true),
            ('Piedras y Accesorios', 20, 4000, true),
            ('French', 10, 2000, true)
        ON CONFLICT DO NOTHING;
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # 4️⃣ CUSTOMERS
    # ═══════════════════════════════════════════════════════════════
    print("👥 Creando clientes...")
    cursor.execute("""
        INSERT INTO customers (name, phone, email)
        VALUES 
            ('Ana García', '3001234567', 'ana.garcia@example.com'),
            ('María López', '3009876543', 'maria.lopez@example.com'),
            ('Laura Martínez', '3005551234', 'laura.martinez@example.com'),
            ('Carolina Rodríguez', '3007778888', 'carolina.rodriguez@example.com'),
            ('Valentina Sánchez', '3002223333', 'valentina.sanchez@example.com')
        ON CONFLICT (email) DO NOTHING;
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # 5️⃣ USERS
    # ═══════════════════════════════════════════════════════════════
    print("🔐 Creando usuario admin...")
    cursor.execute("""
        INSERT INTO users (email, password_hash, name, phone, role)
        SELECT 
            email, 
            password_hash, 
            name, 
            phone, 
            'worker'
        FROM workers
        WHERE email = 'gina.paola@shadysnails.com'
        ON CONFLICT (email) DO NOTHING;
    """)
    
    # Confirmar cambios
    conn.commit()
    
    # ═══════════════════════════════════════════════════════════════
    # VERIFICACIÓN
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("📊 VERIFICACIÓN DE DATOS")
    print("="*60 + "\n")
    
    # Workers
    cursor.execute("SELECT COUNT(*) FROM workers")
    workers_count = cursor.fetchone()[0]
    print(f"✅ Workers: {workers_count}")
    
    # Services
    cursor.execute("SELECT COUNT(*) FROM services")
    services_count = cursor.fetchone()[0]
    print(f"✅ Services: {services_count}")
    
    # Additionals
    cursor.execute("SELECT COUNT(*) FROM additionals")
    additionals_count = cursor.fetchone()[0]
    print(f"✅ Additionals: {additionals_count}")
    
    # Customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    customers_count = cursor.fetchone()[0]
    print(f"✅ Customers: {customers_count}")
    
    # Users
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"✅ Users: {users_count}")
    
    print("\n" + "="*60)
    print("🎉 BASE DE DATOS POBLADA EXITOSAMENTE!")
    print("="*60)
    
    print("\n🔐 CREDENCIALES DE ACCESO:")
    print("   Email: gina.paola@shadysnails.com")
    print("   Password: shadysnails2024")
    print("   Rol: admin/worker")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    
    print("\n✅ Conexión cerrada.")
    
except psycopg2.Error as e:
    print(f"\n❌ Error de base de datos: {e}")
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
