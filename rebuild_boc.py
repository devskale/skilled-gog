#!/usr/bin/env python3
"""
Rebuild BOC (Bootsklemme) document via Google Docs API
Based on SY3 project context and known requirements
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def rebuild_boc_doc(doc_id):
    """Rebuild BOC document with structured content"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    # Clear existing content first
    document = service.documents().get(documentId=doc_id).execute()
    end_index = document.get('body', {}).get('content', [{}])[-1].get('endIndex', 2) - 1

    # Create all content as batch updates
    requests = []

    # Only clear if document has content (more than just the newline)
    if end_index > 2:
        requests.append({
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': end_index
                }
            }
        })

    # 2. Insert content
    content = """BOC Bootsklemme Pflichtenheft

Projekt: SY3 - Elektrischer Außenborder
Datum: 3. Februar 2026
Stand: Entwurf

================================================================

1. Zweck und Anwendung

Die Bootsklemme (Transom Bracket) dient zur Befestigung des elektrischen Außenbordmotors JPS (Jet Pump System) am Spiegel des Bootes.

Anwendung:
- Bootstyp: Elektrisches Wasserfahrzeug (E-Foil / Jetski ähnlich)
- Motor: SY3_JPS (14 Core, Impeller-System)
- Gewicht Motor: 18 kg
- Schaftlänge: 700 mm
- Maximale Schubkraft: ca. 20 kg (≈ 147 N)


2. Technische Anforderungen

2.1 Materialeigenschaften
- salzwasserbeständig
- Festigkeit: (FEM-Berechnung erforderlich)
- Bedienungssicherheit: Fingerschutz

2.2 Aufhängung
- Einfache Handhabung
- Schnelle Montage/Demontage möglich

2.3 Trimmung
- Grad der Aushebung: 12° bzw. 70°
- Verstellbar für verschiedene Fahrzustände


3. Referenzen und Recherche

3.1 Vergleichbare Produkte
- eLite Klemmhalterung: https://maritimo.at/epropulsion-elite-bracket-ersatzteile/
- Untersuchung von marktüblichen Transom Brackets

3.2 CAD-Tools
- tldraw (für Skizzen und Konzeptentwicklung)


4. Berechnungsergebnisse (FEM)

4.1 Lastfälle
- Statische Last: Motor Gewicht (18 kg) am Hebel 700 mm
- Dynamische Last: Schubkraft (20 kg) + Sicherheitsfaktor 2
- Biegemoment durch Motorinstallation

4.2 Randbedingungen
- Verschraubung am Spiegel (Befestigungspunkte definieren)
- Realistische Belastungssimulation

4.3 Erwartete Ergebnisse
- Spannungs- und Verformungsplots
- Sicherheitsfaktor gegen Fließen (≥ 2 für dynamische Lastfälle)
- Identifikation kritischer Stellen


5. Offene Punkte

• Position der Schrauben? Anschraubpunkt
• Maßnahmen Designänderung, die Steifigkeit und Materialverbrauch verbessern
• Gewünschter Hebelarm: 700 mm
• Gewünschte Aushebung: 12° bzw. 70°


6. Lieferumfang

- Konstruktionszeichnungen (CAD)
- FEM-Berechnungsbericht
- Stückliste für Fertigung
- Montageanleitung


7. Kontakt

Bei Fragen zur Auslegung oder FEM-Berechnung:
[Angebotsersteller eintragen]

================================================================

Dokument erstellt: 3. Februar 2026
Letzte Aktualisierung: [Datum eintragen]
"""

    # Insert all content
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    })

    # Apply formatting for headings
    requests.extend([
        # Title
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len('BOC Bootsklemme Pflichtenheft') + 1
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_1',
                    'alignment': 'CENTER'
                },
                'fields': 'namedStyleType,alignment'
            }
        },
        # Subtitle
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': len('BOC Bootsklemme Pflichtenheft') + 2,
                    'endIndex': content.find('================================================================')
                },
                'paragraphStyle': {
                    'namedStyleType': 'NORMAL_TEXT',
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        }
    ])

    # Make headings bold
    sections = [
        '1. Zweck und Anwendung',
        '2. Technische Anforderungen',
        '2.1 Materialeigenschaften',
        '2.2 Aufhängung',
        '2.3 Trimmung',
        '3. Referenzen und Recherche',
        '3.1 Vergleichbare Produkte',
        '3.2 CAD-Tools',
        '4. Berechnungsergebnisse (FEM)',
        '4.1 Lastfälle',
        '4.2 Randbedingungen',
        '4.3 Erwartete Ergebnisse',
        '5. Offene Punkte',
        '6. Lieferumfang',
        '7. Kontakt'
    ]

    for section in sections:
        start_idx = content.find(section)
        if start_idx >= 0:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_idx + 1,
                        'endIndex': start_idx + len(section) + 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2'
                    },
                    'fields': 'namedStyleType'
                }
            })

    # Make bullets under "Offene Punkte"
    open_points_start = content.find('5. Offene Punkte')
    open_points_end = content.find('6. Lieferumfang')
    if open_points_start >= 0 and open_points_end > 0:
        # Find the bullet section
        bullets_section = content.find('• Position', open_points_start)
        if bullets_section >= 0:
            bullets_end = open_points_end
            requests.append({
                'createParagraphBullets': {
                    'range': {
                        'startIndex': bullets_section + 1,
                        'endIndex': bullets_end
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            })

    # Execute batch update
    result = service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    print(f"✓ Document rebuilt: {document.get('title')}")
    print(f"  Total requests: {len(requests)}")
    print(f"  View at: https://docs.google.com/document/d/{doc_id}/edit")

if __name__ == '__main__':
    doc_id = '1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg'
    rebuild_boc_doc(doc_id)
