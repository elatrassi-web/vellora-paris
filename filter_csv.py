import pandas as pd
import os

def filter_csv():
    # Nom du fichier CSV original généré par le scraper
    input_csv = 'yupoo_categorie_4655011.csv'
    output_csv = 'produits_valides.csv'

    if not os.path.exists(input_csv):
        print(f"Erreur: Le fichier {input_csv} n'existe pas dans ce dossier.")
        return

    # Charger le CSV
    df = pd.read_csv(input_csv)

    initial_count = len(df)

    # Filtrer le dataframe : garder la ligne UNIQUEMENT SI le fichier existe dans le chemin spécifié
    df_filtered = df[df['Chemin Local Image'].apply(lambda x: pd.notna(x) and os.path.exists(x))]

    final_count = len(df_filtered)

    # Sauvegarder le nouveau CSV
    df_filtered.to_csv(output_csv, index=False)

    print(f"Filtrage terminé avec succès !")
    print(f"Produits au départ : {initial_count}")
    print(f"Produits restants (images trouvées) : {final_count}")
    print(f"Lignes supprimées : {initial_count - final_count}")
    print(f"Fichier sauvegardé sous : {output_csv}")

if __name__ == "__main__":
    filter_csv()
