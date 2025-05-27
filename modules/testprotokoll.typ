
#set page(
  paper: "a4",
)
#set text(font: "Noto Sans")
#set page(
  margin: (
    top: 4cm,
    left: 2cm,
    right: 1cm,
  ),
  header: {
     grid(
      columns: (2fr, 1fr),
      gutter: 1em,
        align(left)[
          #text("Genossenschaft", size: 8pt) \
          #image("computerbrocki.png", width: 60%)
        ],
        align(left)[
          #text("
          Computerbrockenhaus
          St.Gallerstrasse 18
          8353, Elgg
          info@computerbrocki.ch
          www.computerbrocki.ch", size: 8pt)
        ]
    )
  }
)

#show heading: set text(blue, 26pt)
= Testprotokoll PC und Apple

#let info = csv("system_info.csv")

#table(
  columns: (auto, 1fr),
  inset: 10pt,
  align: horizon,
  ..info.flatten(),
)

