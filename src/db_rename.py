import sqlite3
import os

def rename_study(db_path, old_name, new_name):
    if not os.path.exists(db_path):
        print(f"Błąd: Plik {db_path} nie istnieje!")
        return

    # Kopia zapasowa na wszelki wypadek
    backup_path = db_path + ".bak"
    with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
        dst.write(src.read())
    print(f"Utworzono kopię zapasową: {backup_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Sprawdzamy, czy stare badanie istnieje
        cursor.execute("SELECT study_id FROM studies WHERE study_name = ?", (old_name,))
        result = cursor.fetchone()

        if result:
            # Zmiana nazwy
            cursor.execute("UPDATE studies SET study_name = ? WHERE study_name = ?", (new_name, old_name))
            conn.commit()
            print(f"Sukces! Nazwa '{old_name}' została zmieniona na '{new_name}' wewnątrz bazy.")
        else:
            print(f"Błąd: Nie znaleziono badania o nazwie '{old_name}' w tabeli 'studies'.")
            
            # Podpowiadamy, jakie nazwy są dostępne
            cursor.execute("SELECT study_name FROM studies")
            all_studies = cursor.fetchall()
            if all_studies:
                print("Dostępne badania w tej bazie:")
                for s in all_studies:
                    print(f" - {s[0]}")

    except sqlite3.Error as e:
        print(f"Wystąpił błąd bazy danych: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # PODAJ SWOJE DANE TUTAJ:
    DB_FILE = "optuna_study_bayes_search_model.db"
    OLD_INTERNAL_NAME = "bayes_search_ppo"
    NEW_INTERNAL_NAME = "bayes_search_model"

    rename_study(DB_FILE, OLD_INTERNAL_NAME, NEW_INTERNAL_NAME)