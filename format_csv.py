import pandas as pd

df = pd.read_csv('yupoo_shopify_import_100.csv')

# Only keep the rows that have a Title (these are the main product rows, not the variant rows)
simple_df = df[df['Title'].notna() & (df['Title'] != '')].copy()

# The user explicitly asked for Titre, Prix, Image URL.
# Let's provide a clean simplified CSV.
cols_to_keep = ['Title', 'Variant Price', 'Image Src']
simple_df = simple_df[cols_to_keep]
simple_df.columns = ['Titre', 'Prix', 'URL Image']

simple_df.to_csv('yupoo_produits_100.csv', index=False)
print("Saved simple CSV yupoo_produits_100.csv")
