#!/usr/bin/env python3
"""Send a joke email from Uncle Fritz."""
from google_workspace_tools.gmail import send_message

TO = "melanie.kirschner@gmail.com"
SUBJECT = "Witz vom Onkel Fritz 🎩"
BODY = """Liebe Melanie,

Onkel Fritz war beim Arzt und der fragte ihn: "Und, wie geht's Ihnen denn so?"

Onkel Fritz lehnte sich zurück und fing an: "Na, wissen Se, Herr Doktor, das ist so 'ne Sache. Vorgestern, das war doch Mittwoch, da bin ich morgens aufgewacht und mein linkes Knie hat geklickt. Nichts Schlimmes, nur so 'klick', wie wenn man 'ne Stiftfeder spannt. Dachte ich mir nichts bei', bin aufgestanden, und was passiert? Der linke Fuß ist eingeschlafen!

Ich hoffe zwar, das geht vorbei, aber dann fängt mein rechter Fuß auch an zu kribbeln. Jetzt steh ich da wie auf Ameisen, und meine Frau schreit von unten: 'Fritz, das Frühstück wird kalt!' - dabei ist gar kein Frühstück, die hatte das verwechselt mit dem Abendbrot vom Vortag.

Jedenfalls humpel ich die Treppe runter, und mein Knie macht bei jeder Stufe 'klick-klick-klick', wie so 'ne alte Uhr. Der Hund schaut mich so komisch an, und der Papagei ruft 'Hilfe, Erdbeben!' - dabei war's nur ich.

Dann sitz ich am Tisch, und meine Frau sagt: 'Fritz, du siehst blass aus.' - 'Ja', sag ich, 'mein Knie klickt und meine Füße kribbeln.' Da sagt sie: 'Das kommt vom Wetter, Onkel Wilhelm hatte das auch immer.' - Onkel Wilhelm! Der ist doch seit 30 Jahren tot, und der hatte überhaupt keine Knie, der war im Krieg verwundet!

Aber gut, ich esse mein Frühstück - oder war's Abendbrot? - und dann klingelt das Telefon. Wer war's? Die Tante Erna aus Buxtehude! Die ich seit der Kommunion 1954 nicht mehr gesehen hab! Und die fragt mich: 'Na Fritzchen, wie geht's dem Knie?' - Woher wusste die das?! Ich frag's sie, und sie sagt: 'Ich hab mich mit deiner Frau unterhalten, die hat's mir erzählt.' - Meine Frau telefoniert mit Tante Erna, während ich auf Ameisenfüßen durch die Küche laufe!

Und jetzt komm ich zu Ihnen, Herr Doktor, und Sie fragen mich, wie's mir geht. Und ich sag Ihnen: Wenn mein Knie klickt, weiß ich, dass ich noch leb. Wenn die Füße kribbeln, weiß ich, dass noch Durchblutung da ist. Wenn meine Frau sich mit Tante Erna über mich unterhält, weiß ich, dass ich geliebt werd. Und wenn ich bei Ihnen sitze, Herr Doktor, dann weiß ich, dass ich hoffentlich noch nicht tot bin!

Der Doktor schaute ihn lange an und sagte: 'Herr Fritz, Sie sind kerngesund. Ihr Knie klickt, weil Sie samstags immer im Garten knien. Ihre Füße kribbeln, weil Sie Ihre Socken waschen und nicht spülen. Und dass Ihre Frau mit Tante Erna redet... tja, das ist halt Familie.'

Da hat Onkel Fritz gelacht und gesagt: 'Wissen Sie was, Herr Doktor? Das ist der beste Witz, den ich je gehört hab!' - 'Witz?', fragte der Doktor. 'Welcher Witz?' - 'Na der, dass ich kerngesund bin!'

Die Moral von der Geschicht: Manchmal ist Gesundheit der größte Witz vom Onkel Fritz! 🎭

Herzliche Grüße,
Dein Lieblings-Onkel

---

PS: Der Papagei übrigens hat nach dem 'Erdbeben' angefangen, 'klick-klick-klick' zu pfeifen. Der lernt eben schnell! 🦜
"""

if __name__ == "__main__":
    print(f"Sende E-Mail an {TO}...")
    result = send_message(TO, SUBJECT, BODY)
    print(f"E-Mail gesendet! ID: {result.get('id', 'unbekannt')}")
