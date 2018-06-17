from flask import Flask, request, make_response, render_template
import mysql.connector
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO, Entrez
import time

app = Flask(__name__)

@app.route('/')
def home():
    resp = make_response(render_template('home.html'))
    return resp

@app.route('/tabel')
def zoeken_tabel():
    default = ''
    zoekopdracht_eiwitfunctie = request.args.get("zoekopdracht_eiwitfunctie", default)
    zoekopdracht_acc_code = request.args.get("zoekopdracht_acc_code", default)
    zoekopdracht_soorten = request.args.get("zoekopdracht_soorten", default)

    # Een connectie om de tabel namen op te vragen
    conn = mysql.connector.connect(host='sql7.freemysqlhosting.net', user='sql7241830', passwd='gcSSIhcVul',
                                     db='sql7241830')

    # Cursor met andere naam wordt gemaakt voor de connectie. En andere query wordt uitgevoerd tegen de database
    cursor = conn.cursor()  # cursor wordt gemaakt voor connectie

    sql = """SELECT accession_code, protein_function, species, protein_sequence FROM PROTEINS NATURAL JOIN RESULTS LIMIT 100;"""

    if zoekopdracht_eiwitfunctie != default or zoekopdracht_acc_code != default or zoekopdracht_soorten != default:
        sql = sql[:-10] + "WHERE "

    # sql die word aangeroepen bij invoer zoekopdracht_eiwitfunctie
    if zoekopdracht_eiwitfunctie != default:
        count = 0
        sql_eiwit = '('
        zoekopdracht_eiwitfunctie = list(zoekopdracht_eiwitfunctie.split(', '))
        for zoekwoord in zoekopdracht_eiwitfunctie:
            count += 1
            zoekwoord = "\'%" + zoekwoord + "%\'"
            if count == len(zoekopdracht_eiwitfunctie):
                sql_eiwit += "protein_function LIKE {}) ".format(zoekwoord)
            else:
                sql_eiwit += "protein_function LIKE {} OR ".format(zoekwoord)
        sql += "AND " + sql_eiwit

    if zoekopdracht_acc_code != default:
        count = 0
        sql_acc_code = '('
        zoekopdracht_acc_code = list(zoekopdracht_acc_code.split(', '))
        for zoekwoord in zoekopdracht_acc_code:
            count += 1
            zoekwoord = "\'%" + zoekwoord + "%\'"
            if count == len(zoekopdracht_acc_code):
                sql_acc_code += "accession_code LIKE {}) ".format(zoekwoord)
            else:
                sql_acc_code += "accession_code LIKE {} OR ".format(zoekwoord)
        sql += "AND " + sql_acc_code

    if zoekopdracht_soorten != default:
        count = 0
        sql_soorten = '('
        zoekopdracht_soorten = list(zoekopdracht_soorten.split(', '))
        for zoekwoord in zoekopdracht_soorten:
            count += 1
            zoekwoord = "\'%" + zoekwoord + "%\'"
            if count == len(zoekopdracht_soorten):
                sql_soorten += "species LIKE {}) ".format(zoekwoord)
            else:
                sql_soorten += "species LIKE {} OR ".format(zoekwoord)
        sql += "AND " + sql_soorten

    if zoekopdracht_eiwitfunctie != default or zoekopdracht_acc_code != default or zoekopdracht_soorten != default:
        sql = sql[:107] + sql[111:]

    cursor.execute(sql)


    resp = make_response(render_template('tabel.html', zoekopdracht_eiwitfunctie=zoekopdracht_eiwitfunctie,
                                         zoekopdracht_soorten=zoekopdracht_soorten,
                                         zoekopdracht_acc_code=zoekopdracht_acc_code, cursor=cursor))  # maakt een rspons aan voor de template
    cursor.close()
    conn.close()
    return resp  #Alle conecties worden worden gesloten                                                                                                    #Alle conecties worden worden gesloten
    

@app.route('/blast')
def blasten():
    blast_opdracht = request.args.get("blast",'')
    conn = mysql.connector.connect(host='sql7.freemysqlhosting.net', user='sql7241830',
                                   passwd='gcSSIhcVul', db='sql7241830')
    counter = 200
    try:
        if blast_opdracht != '':
            result_handle = NCBIWWW.qblast("blastx", "nr", blast_opdracht, matrix_name='BLOSUM62',
                                           gapcosts='11 1', word_size=6, hitlist_size=5, expect=0.000001)

            blast_resultaten = NCBIXML.read(result_handle)

            Entrez.email = 'lisa.kuipers26@hotmail.com'
            for alignment in blast_resultaten.alignments:
                genbank_annotation = True
                soort = 'unknown'
                accession = alignment.accession
                handle = Entrez.efetch(db='protein', id=accession, rettype='gp', retmode='text')
                record = SeqIO.read(handle, 'genbank')
                eiwit_naam = record.id
                eiwit_functie = record.description
                eiwit_sequentie = str(record.seq)
                soort = record.annotations['organism']
                genus = record.annotations['taxonomy'][-1]
                familie = record.annotations['taxonomy'][-2]

                protein_id = None
                genus_id = None


            resp = make_response(render_template('blast.html',eiwit_naam=eiwit_naam,eiwit_functie=eiwit_functie,
                                                     eiwit_sequentie=eiwit_sequentie,soort=soort,genus=genus, familie=familie))
            return resp

        else:
            respons_leeg = make_response(render_template('blast.html'))
            return respons_leeg

    except OSError:
        oeps = make_response(render_template('oeps.html'))
        return oeps


@app.route('/about')
def about():
    resp = make_response(render_template('about.html'))
    return resp

if __name__ == '__main__':
    app.run(debug=True)
