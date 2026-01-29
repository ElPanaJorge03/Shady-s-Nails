import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📊 Verificando tablas en: {DATABASE_URL}\n")

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    
    if tables:
        print(f"✅ Se encontraron {len(tables)} tablas:\n")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
            
            # Mostrar columnas de cada tabla
            columns = inspector.get_columns(table)
            print(f"     Columnas ({len(columns)}):")
            for col in columns[:5]:  # Mostrar solo las primeras 5 columnas
                print(f"       - {col['name']} ({col['type']})")
            if len(columns) > 5:
                print(f"       ... y {len(columns) - 5} más")
            print()
    else:
        print("⚠️ No se encontraron tablas en la base de datos")
        
except Exception as e:
    print(f"❌ Error: {e}")
