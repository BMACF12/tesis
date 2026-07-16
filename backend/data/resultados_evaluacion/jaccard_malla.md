# Completitud / Jaccard de las mallas curriculares (Indicador 3)

Evaluador: `scripts/completitud_malla.py` (reconstruccion por coordenadas, sin ChromaDB ni LLM).

## Esquema comparado (universo A) por malla

Por CADA asignatura reconstruida se comparan **4 campos** (los que pueden salir `VACIO`):

1. `nombre`
2. `prerrequisito`
3. `hpao`
4. `creditos`

Mas la **estructura del pensum**: los **8 PAO** (Primer ... Octavo). Universo `A = 4 x nº_asignaturas + 8`. `Jaccard = |rellenado| / |A|`.

El **codigo** de asignatura es el ANCLA/identificador (la malla no lleva NRC): siempre presente por construccion, se reporta pero NO puntua como campo vacio.

El invariante **HPAO = 48 x creditos** se controla aparte: una violacion es una ANOMALIA que se reporta, NO un campo vacio.

Leyenda de estado por campo: `✓` relleno / `✗` VACIO.

---

## malla isoj 202450 act.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_233708.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla trampa_20260702_105057.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla_ingenierIa_de_software.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | NTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | CURRCULAR | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Calculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0J01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0G01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación Científica | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Calculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0J08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0J09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0F03   | nombre[✓]=Modelos Discretos para Ingeniería SO | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
COMPA0I01   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G06   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0H02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0J09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G04   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0J11   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0H04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0G09   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0G07 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0G10   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0J13   | nombre[✓]=Computacion Gráfica | prerrequisito[✓]=EXCTA0303 O EXCTA0001 | hpao[✓]=96 | creditos[✓]=2
COMPA0K01   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0I07   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0L03   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0J09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G15   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0G11   | nombre[✓]=Análisis y diseño de software | prerrequisito[✓]=COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0I08   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0K03   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0G12   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0G18   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0G16   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0I09   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0J14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0L03 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0G19   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0G15 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0G23   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0G21   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0G16 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0G24   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=COMPAG018 | hpao[✓]=96 | creditos[✓]=2
COMPA0G25   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 (3)_20260703_002804.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 (3)_20260703_011305.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 (4)_20260703_002014.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 (4)_20260703_010848.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act (2)_20260703_002140.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act (2)_20260703_011013.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act (5) - copia_20260703_003404.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act (5)_20260703_002304.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act (5)_20260703_003105.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260621_233530.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_232636.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_233113.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_233410.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_233708_20260715_201157.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_233944.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_234229.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_234518.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_234908.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260701_235202.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260702_001804.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260702_104932.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260702_235742.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260703_002429.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260703_003235.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260706_004510.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260706_005042.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260706_011031.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260706_012019.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260709_135144.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla isoj 202450 act_20260715_201227.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla trampa_20260702_105057_20260715_201212.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | CURRCULARNTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Cálculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0P01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0M01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Cálculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0P08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0P01 O COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0P09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0P08 O COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0N09   | nombre[✓]=Modelos Discretos para Ingeniería | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0401 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
ELEEA0442   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0P01 O COMPA0J01 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M05   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M03   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0M01 O COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0R12   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0P09 O COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0N04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0N02 O COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0R04   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0R02 O COMPA0G07 O COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0M06   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0M05 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0P13   | nombre[✓]=Computación Gráfica | prerrequisito[✓]=EXCTA0001 O EXCTA0303 | hpao[✓]=96 | creditos[✓]=2
COMPA0T08   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0S05   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=ELEEA0442 O COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0N10   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0P09 O COMPA0J09 O COMPA0N09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0M08   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0M07   | nombre[✓]=Análisis y Diseño de Software | prerrequisito[✓]=COMPA0M06 O COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0S06   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0S05 O COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0T14   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0T08 O COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0P16   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0M09   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPAM08 [CÓDIGO MALFORMADO] O COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0R07   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0R04 O COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0S07   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0S06 O COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0P14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0N10 O COMPA0L03 O COMPA0P13 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0S13   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0M08 O COMPA0G15 O COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0M10   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0M09 O COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0R10   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0R07 O COMPA0G16 O COMPA0S13 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0M11   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0S07 O COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=SEGDA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0T10   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0M07 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

## malla_ingenierIa_de_software_20260715_201239.pdf

- **Jaccard**: 1.000  (|B|=184 / |A|=184)
- **Asignaturas reconstruidas**: 44
- **PAO detectados**: 8/8
- **Anomalias HPAO=48xCR**: 0
- **Niveles/unidades leidos**: UNDADDE | NTEGRACÓN | UNDADPROFESONAL | UNDADBASCA | CURRCULAR | OctavoPAO | SeptimoPAO | SextoPAO | QuntoPAO | CuartoPAO | TercerPAO | SegundoPAO | PrimerPAO

### Lista completa de elementos comparados

Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`

```
EXCTA0301   | nombre[✓]=Calculo Diferencial e Integral | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0201   | nombre[✓]=Química I | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
COMPA0J01   | nombre[✓]=Fundamentos de Programación | prerrequisito[✓]=NIVELACION | hpao[✓]=144 | creditos[✓]=3
EXCTA0302   | nombre[✓]=Álgebra Lineal | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
COMPA0G01   | nombre[✓]=Fundamentos de la Ingeniería de Software | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
CHUMA0100   | nombre[✓]=Metodología de la Investigación Científica | prerrequisito[✓]=NIVELACION | hpao[✓]=96 | creditos[✓]=2
EXCTA0303   | nombre[✓]=Calculo Vectorial | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0001   | nombre[✓]=Física I | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0401   | nombre[✓]=Ecuaciones Diferenciales Ordinarias | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
SEGDA0000   | nombre[✓]=Liderazgo | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0J08   | nombre[✓]=Programación Orientada a Objetos | prerrequisito[✓]=COMPA0J01 | hpao[✓]=192 | creditos[✓]=4
COMPA0J09   | nombre[✓]=Estructura de Datos | prerrequisito[✓]=COMPA0J08 | hpao[✓]=144 | creditos[✓]=3
COMPA0F03   | nombre[✓]=Modelos Discretos para Ingeniería SO | prerrequisito[✓]=EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0501   | nombre[✓]=Estadística | prerrequisito[✓]=EXCTA0301 O EXCTA0302 | hpao[✓]=144 | creditos[✓]=3
EXCTA0402   | nombre[✓]=Métodos Numéricos | prerrequisito[✓]=EXCTA0401 | hpao[✓]=96 | creditos[✓]=2
TCONA0304   | nombre[✓]=Cultura Ambiental | prerrequisito[✓]=N/A | hpao[✓]=96 | creditos[✓]=2
SEGDA0100   | nombre[✓]=Realidad Nacional y Geopolítica | prerrequisito[✓]=SEGDA0000 | hpao[✓]=96 | creditos[✓]=2
COMPA0I01   | nombre[✓]=Computación Digital | prerrequisito[✓]=COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G06   | nombre[✓]=Modelos de Procesos de Desarrollo de Software | prerrequisito[✓]=COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0H02   | nombre[✓]=Sistemas de Bases de Datos | prerrequisito[✓]=COMPA0J09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G04   | nombre[✓]=Ingeniería de Usabilidad | prerrequisito[✓]=COMPA0G01 | hpao[✓]=96 | creditos[✓]=2
COMPA0J11   | nombre[✓]=Computación Paralela | prerrequisito[✓]=COMPA0J09 | hpao[✓]=96 | creditos[✓]=2
COMPA0H04   | nombre[✓]=Sistemas Avanzados de Bases de Datos | prerrequisito[✓]=COMPA0H02 | hpao[✓]=144 | creditos[✓]=3
COMPA0G09   | nombre[✓]=Desarrollo Web Avanzado | prerrequisito[✓]=COMPA0G07 O COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0G10   | nombre[✓]=Ingenieria de Requisitos de Software | prerrequisito[✓]=COMPA0G06 | hpao[✓]=144 | creditos[✓]=3
COMPA0J13   | nombre[✓]=Computacion Gráfica | prerrequisito[✓]=EXCTA0303 O EXCTA0001 | hpao[✓]=96 | creditos[✓]=2
COMPA0K01   | nombre[✓]=Investigación en la Ingeniería de Software | prerrequisito[✓]=CHUMA0100 | hpao[✓]=96 | creditos[✓]=2
COMPA0I07   | nombre[✓]=Redes de Computadores | prerrequisito[✓]=COMPA0I01 | hpao[✓]=96 | creditos[✓]=2
COMPA0L03   | nombre[✓]=Aplicaciones Basadas en el Conocimiento | prerrequisito[✓]=COMPA0J09 O COMPA0F03 | hpao[✓]=144 | creditos[✓]=3
COMPA0G15   | nombre[✓]=Pruebas de Software | prerrequisito[✓]=COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0G11   | nombre[✓]=Análisis y diseño de software | prerrequisito[✓]=COMPA0G10 | hpao[✓]=96 | creditos[✓]=2
COMPA0I08   | nombre[✓]=Sistemas Operativos | prerrequisito[✓]=COMPA0I07 | hpao[✓]=96 | creditos[✓]=2
COMPA0K03   | nombre[✓]=Lectura y Escritura de Textos Académicos | prerrequisito[✓]=COMPA0K01 | hpao[✓]=96 | creditos[✓]=2
COMPA0G12   | nombre[✓]=Desarrollo de Aplicaciones Móviles | prerrequisito[✓]=COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0G18   | nombre[✓]=Aseguramiento de la Calidad de Software | prerrequisito[✓]=COMPA0G15 | hpao[✓]=96 | creditos[✓]=2
COMPA0G16   | nombre[✓]=Aplicaciones Distribuidas | prerrequisito[✓]=COMPA0G09 | hpao[✓]=96 | creditos[✓]=2
COMPA0I09   | nombre[✓]=Ingeniería de la Seguridad del Software | prerrequisito[✓]=COMPA0I08 | hpao[✓]=96 | creditos[✓]=2
COMPA0J14   | nombre[✓]=Desarrollo de Video Juegos | prerrequisito[✓]=COMPA0L03 O COMPA0J13 | hpao[✓]=96 | creditos[✓]=2
COMPA0G19   | nombre[✓]=Desarrollo de Software Seguro | prerrequisito[✓]=COMPA0G15 O COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
COMPA0G23   | nombre[✓]=Construcción y Evolución del Software | prerrequisito[✓]=COMPA0G18 | hpao[✓]=96 | creditos[✓]=2
COMPA0G21   | nombre[✓]=Arquitectura de Software | prerrequisito[✓]=COMPA0G16 O COMPA0G19 | hpao[✓]=96 | creditos[✓]=2
COMPA0G24   | nombre[✓]=Desarrollo de Software Aplicado al Dominio de la Interculturalidad | prerrequisito[✓]=COMPA0I09 | hpao[✓]=96 | creditos[✓]=2
CADMA0G00   | nombre[✓]=Gestión y Emprendimiento | prerrequisito[✓]=COMPAG018 | hpao[✓]=96 | creditos[✓]=2
COMPA0G25   | nombre[✓]=Gestión de Proyectos de Software | prerrequisito[✓]=COMPA0G11 | hpao[✓]=96 | creditos[✓]=2
```

### 8 PAO (estructura del pensum)

✓ Primer  ✓ Segundo  ✓ Tercer  ✓ Cuarto  ✓ Quinto  ✓ Sexto  ✓ Séptimo  ✓ Octavo

---

# Resumen del corpus

| Malla | Jaccard | Asig | PAO | Anom. HPAO | Faltantes |
|-------|--------:|-----:|----:|-----------:|----------:|
| malla isoj 202450 act.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_233708.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla trampa_20260702_105057.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla_ingenierIa_de_software.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 (3)_20260703_002804.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 (3)_20260703_011305.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 (4)_20260703_002014.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 (4)_20260703_010848.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act (2)_20260703_002140.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act (2)_20260703_011013.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act (5) - copia_20260703_003404.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act (5)_20260703_002304.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act (5)_20260703_003105.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260621_233530.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_232636.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_233113.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_233410.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_233708_20260715_201157.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_233944.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_234229.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_234518.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_234908.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260701_235202.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260702_001804.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260702_104932.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260702_235742.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260703_002429.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260703_003235.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260706_004510.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260706_005042.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260706_011031.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260706_012019.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260709_135144.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla isoj 202450 act_20260715_201227.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla trampa_20260702_105057_20260715_201212.pdf | 1.000 | 44 | 8/8 | 0 | 0 |
| malla_ingenierIa_de_software_20260715_201239.pdf | 1.000 | 44 | 8/8 | 0 | 0 |

- **Mallas evaluadas**: 36
- **Mallas completas (J = 1.000)**: 36 de 36
- **Jaccard medio**: 1.000
- **PDFs descartados (no es una malla)**: 12
  - MALLA-EDUCACION-INICIAL-EN-LINEA.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_E_20260708_183950.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_181902.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_182052.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_182321.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_182430.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_182609.pdf
  - Silabo_NRC-21379_Desarrollo_Aplicaciones_Moviles_Edwin_Chasiquiza_DASyAS_VI_Software_202550-signed-signed - copia_20260708_183046.pdf
  - silabo_tachadoo_20260708_182116.pdf
  - silabo_tachadoo_20260708_182634.pdf
  - silabo_tachadoo_20260708_183114.pdf
  - silabo_tachadoo_20260708_184015.pdf
