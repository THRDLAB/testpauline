from flask import Flask, jsonify, redirect, request
import psycopg2

app = Flask(__name__)

# Configuration de la connexion à PostgreSQL
conn = psycopg2.connect(
    host="primary.thyroresearch-ddb--kl8x797qxrg2.addon.code.run",
    port="29647",
    database="pubmed",
    user="_6865d85393a52a7f",
    password="_e5407dde3a89a0756343cba1a7eaf1"
)

@app.route('/')
def index():
    # Redirection vers l'endpoint /latest-articles
    return redirect('/latest-articles')

@app.route('/latest-articles', methods=['GET'])
def get_latest_articles():
    try:
        cur = conn.cursor()

        # Récupération des 4 derniers articles sans doublons dans les nct_id
        query = """
            SELECT DISTINCT ON (a.pmid) 
                a.pmid, a.title, a.entrez_date, 
                au.lastname, 
                c.condition, c.category, 
                pt.population_type, 
                pbt.publication_type
            FROM articles a
            LEFT JOIN authors au ON a.pmid = au.pmid
            LEFT JOIN conditions c ON a.pmid = c.pmid
            LEFT JOIN population_type pt ON a.pmid = pt.pmid
            LEFT JOIN publication_type pbt ON a.pmid = pbt.pmid
            ORDER BY a.pmid, a.entrez_date DESC
            LIMIT 4
        """
        cur.execute(query)
        latest_articles_data = cur.fetchall()

        cur.close()

        # Formatage des données pour avoir toutes les informations sur une seule ligne
        combined_data = []
        for row in latest_articles_data:
            article = {
                'pmid': row[0],
                'title': row[1],
                'entrez_date': row[2],
                'lastname': row[3],
                'condition': row[4],
                'category': row[5],
                'population_type': row[6],
                'publication_type': row[7]
            }
            combined_data.append(article)

        return jsonify(combined_data)

    except psycopg2.Error as e:
        conn.rollback()  # Rollback pour annuler la transaction courante
        return f"Erreur PostgreSQL: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

