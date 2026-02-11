#!/usr/bin/env python3
"""
Script para verificar dados no banco de dados PostgreSQL do Railway
"""
import psycopg
from datetime import datetime
import sys

# Credenciais do banco Railway
# SUBSTITUA 'SUA_SENHA_AQUI' pela senha real do PostgreSQL no Railway
DB_CONFIG = {
    "host": "hopper.proxy.rlwy.net",
    "port": 39796,
    "database": "railway",  # ou "betting_bot" - verifique no Railway qual é o nome correto
    "user": "postgres",
    "password": "LdiOhZUOlAHgRHyEoarzghhWThFlJfCM"  # ⚠️ SUBSTITUA AQUI
}

def check_database():
    """Conecta ao banco e verifica os dados das odds"""
    
    print("=" * 80)
    print("🔍 VERIFICANDO BANCO DE DADOS NO RAILWAY")
    print("=" * 80)
    print(f"📍 Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"📦 Database: {DB_CONFIG['database']}")
    print(f"👤 User: {DB_CONFIG['user']}")
    print()
    
    try:
        # Conecta ao banco
        print("🔌 Conectando ao banco...")
        conn = psycopg.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        print("✅ Conexão estabelecida com sucesso!\n")
        
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        print("📋 TABELAS DISPONÍVEIS:")
        print("-" * 80)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Verifica a tabela de odds (pode ter nomes diferentes)
        possible_odds_tables = ['odds', 'events', 'matches', 'arbitrage_opportunities']
        
        for table_name in possible_odds_tables:
            try:
                # Conta registros
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"📊 TABELA: {table_name}")
                print(f"   Total de registros: {count}")
                
                if count > 0:
                    # Mostra últimos 10 registros
                    cursor.execute(f"""
                        SELECT * FROM {table_name} 
                        ORDER BY created_at DESC 
                        LIMIT 10;
                    """)
                    rows = cursor.fetchall()
                    
                    # Mostra colunas
                    columns = [desc[0] for desc in cursor.description]
                    print(f"   Colunas: {', '.join(columns)}")
                    print(f"   Últimos 10 registros:")
                    
                    for i, row in enumerate(rows, 1):
                        print(f"\n   [{i}]")
                        for col, val in zip(columns, row):
                            # Trunca valores muito longos
                            val_str = str(val)
                            if len(val_str) > 100:
                                val_str = val_str[:100] + "..."
                            print(f"      {col}: {val_str}")
                    print()
                    
            except psycopg.Error as e:
                if "does not exist" not in str(e):
                    print(f"   ⚠️ Erro ao consultar {table_name}: {e}\n")
                continue
        
        # Verifica registros recentes (últimas 24h)
        print("🕐 REGISTROS DAS ÚLTIMAS 24 HORAS:")
        print("-" * 80)
        for table_name in possible_odds_tables:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE created_at >= NOW() - INTERVAL '24 hours';
                """)
                recent_count = cursor.fetchone()[0]
                if recent_count > 0:
                    print(f"   {table_name}: {recent_count} novos registros")
            except:
                continue
        
        print()
        cursor.close()
        conn.close()
        print("✅ Verificação concluída com sucesso!")
        
    except psycopg.Error as e:
        print(f"❌ ERRO AO CONECTAR AO BANCO:")
        print(f"   {str(e)}")
        print()
        print("💡 DICAS:")
        print("   1. Verifique se a senha está correta no DB_CONFIG")
        print("   2. Confirme o nome do banco (railway ou betting_bot)")
        print("   3. Verifique se o IP está liberado no firewall do Railway")
        print("   4. No Railway, vá em PostgreSQL > Settings > verificar credenciais")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO: Edite este arquivo e substitua 'SUA_SENHA_AQUI' pela senha real!\n")
    
    if DB_CONFIG["password"] == "SUA_SENHA_AQUI":
        print("❌ Você precisa editar o arquivo e adicionar a senha do banco PostgreSQL!")
        print("   Encontre a senha no Railway em: PostgreSQL > Connect > Password")
        sys.exit(1)
    
    check_database()
