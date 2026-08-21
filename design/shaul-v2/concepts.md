---
title: "Shaul v2: mapa inicial de conceptos"
description: "Catálogo de 50 conceptos transversales para la nueva presentación de Shaul, con conexiones a versículos y notas existentes."
date: 2026-08-13
tags:
  - shaul-v2
  - conceptos
  - diseño
  - canon
references: []
sources:
  - "content/"
  - "docs/note-authoring.md"
---

# Shaul v2: mapa inicial de conceptos

## Propósito de esta primera iteración

La propuesta es que la página no comience únicamente por una lista cronológica de notas, sino por un mapa de conceptos que permita entrar por una palabra o una idea y recorrer sus conexiones. Cada concepto puede abrir un **card** breve: una tesis en lenguaje humano, tres o cuatro párrafos de explicación y una red de conexiones verificables.

Las conexiones se separan en dos clases:

- **Versículos:** anclas bíblicas que se pueden abrir directamente en el índice de Escrituras.
- **Notas:** estudios de Shaul que desarrollan el concepto y permiten volver al contexto completo de la enseñanza.

Este archivo es un catálogo editorial. La redacción de los cincuenta cards está en `design/shaul-v2/cards-50.md` y se funda en las tesis de las notas, no en definiciones genéricas. Este mapa conserva la vista compacta para el grafo, los filtros y la navegación.

## Criterio de selección

Los conceptos fueron escogidos por su recurrencia en las notas de Besorah, Tanaj y Temas. No se intenta resumir toda la teología en cincuenta palabras ni cerrar interpretaciones que el conocimiento interno deja abiertas. Cada card conserva la diferencia entre lo que el texto afirma, la conexión canónica que se propone y lo que aún queda pendiente de verificar.

## Los 50 conceptos propuestos

|   # | Slug                | Concepto                                     | Eje                   | Notas de partida                                                                                                                                                        |
| --: | ------------------- | -------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|   1 | `ben-hadam`         | Ben-Hadam / Hijo del Hombre                  | Identidad del Mesías  | `content/besorah/markos_ben_adam_metamorfosis_glosario.md`; `content/besorah/yojanan_9_ben_adam_y_el_ciego.md`; `content/temas/ben_hijo_titulos_mesias.md`               |
|   2 | `palabra`           | La Palabra que crea, revela y permanece      | Revelación            | `content/besorah/markos_palabra_trono_semilla_identidad.md`; `content/besorah/yojanan_introduccion.md`                                                                  |
|   3 | `hijo-elohim`       | Hijo de Elohim y herencia                    | Identidad y filiación | `content/besorah/markos_hijo_elohim_hijo_hombre_herencia.md`; `content/temas/ben_hijo_titulos_mesias.md`                                                                |
|   4 | `abba`              | Abá: fuente, envío y obediencia              | Relación con Elohim   | `content/temas/elohim_aba.md`; `content/besorah/markos_abba_ruaj_mente_mashiaj.md`; `content/besorah/yojanan_oracion_dos_tronos_emunah.md`                               |
|   5 | `ruaj`              | Ruaj: presencia, santidad y vida             | Presencia             | `content/temas/elohim_presencia_ruaj_neshamah.md`; `content/temas/ruaj_haqodesh_santidad_presencia_y_evangelio.md`                                                      |
|   6 | `mashiaj`           | El Mesías como centro de la lectura          | Mesianismo            | `content/temas/mashiaj_esperanza_de_israel_y_redencion.md`; `content/temas/identidad_mesianica_tora_gracia_y_discernimiento.md`                                         |
|   7 | `torah-y-gracia`    | Torah y gracia sin oposición artificial      | Pacto                 | `content/besorah/romanos_3_ley_pecado_justicia_y_fe.md`; `content/temas/613_mitzvot_contexto_obligacion_y_justificacion.md`; `content/temas/abolicion_de_la_tora_sentencia_pecado_y_plenitud_del_mesias.md` |
|   8 | `reino`             | Reino, autoridad y servicio                  | Gobierno              | `content/besorah/markos_10_pacto_reino_riqueza_servicio_camino.md`; `content/besorah/yojanan_17_gloria_autoridad_y_vida.md`                                             |
|   9 | `vida`              | Vida que vence la muerte                     | Vida                  | `content/besorah/yojanan_5_hijo_juicio_vida.md`; `content/besorah/romanos_8_vida_en_el_Ruaj_filiacion_sufrimiento_esperanza.md`                                         |
|  10 | `luz`               | Luz, testimonio y discernimiento             | Testimonio            | `content/besorah/yojanan_8_luz_testimonio_y_abraham.md`; `content/besorah/efesios_5_amor_luz_y_sabiduria.md`                                                            |
|  11 | `pan-de-vida`       | Pan, sustento y palabras de vida             | Provisión             | `content/besorah/yojanan_6_pan_de_vida_y_palabras_de_vida.md`; `content/besorah/yojanan_6_pan_vida_senales.md`                                                          |
|  12 | `agua-viva`         | Agua viva, purificación y adoración          | Renovación            | `content/besorah/yojanan_4_estudio_canonico_agua_viva_adoracion_y_confianza.md`; `content/besorah/yojanan_7_sucot_agua_y_discernimiento.md`                             |
|  13 | `morada`            | Morada, presencia y regreso                  | Presencia             | `content/besorah/yojanan_14_moradas_camino_retorno.md`; `content/besorah/yojanan_14_morada_palabra_memoria.md`                                                          |
|  14 | `puerta`            | La puerta, el acceso y el cuidado            | Comunidad             | `content/besorah/yojanan_10_puerta_pastor_abba.md`; `content/besorah/yojanan_9_10_ceguera_puerta_ovejas.md`                                                             |
|  15 | `pastor`            | Pastor, ovejas y cuidado del rebaño          | Comunidad             | `content/temas/pastor_ovejas_discernimiento_y_cuidado_del_rebano.md`; `content/besorah/yojanan_10_pastor_vida_obras.md`                                                 |
|  16 | `ovejas`            | Escucha, reconocimiento y seguimiento        | Discipulado           | `content/besorah/yojanan_10_emunah_obras_ovejas.md`; `content/temas/pastor_ovejas_discernimiento_y_cuidado_del_rebano.md`                                               |
|  17 | `cuerpo-del-mesias` | Un cuerpo, muchos miembros y una cabeza      | Comunidad             | `content/besorah/efesios_4_llamado_unidad_y_vida_nueva.md`; `content/besorah/colosenses_2_plenitud_discernimiento_y_cabeza.md`                                          |
|  18 | `unidad`            | Unidad que se practica en verdad             | Comunidad             | `content/besorah/efesios_2_lejania_paz_y_un_solo_pueblo.md`; `content/besorah/romanos_14_acogida_mutua_conciencia_edificacion.md`                                       |
|  19 | `reconciliacion`    | Reconciliación y un solo pueblo              | Pacto                 | `content/besorah/efesios_2_lejania_paz_y_un_solo_pueblo.md`; `content/temas/israel_no_reemplazado_un_pueblo_y_un_olivo.md`; `content/besorah/colosenses_1_sabiduria_herencia_plenitud.md` |
|  20 | `pueblo`            | Pueblo, herencia y pertenencia               | Identidad             | `content/temas/israel_no_reemplazado_un_pueblo_y_un_olivo.md`; `content/temas/613_mitzvot_semilla_de_yisrael_y_limites_de_pertenencia.md`; `content/besorah/efesios_3_gracia_revelacion_y_misterio.md` |
|  21 | `semilla`           | Semilla, palabra e identidad                 | Crecimiento           | `content/besorah/markos_palabra_trono_semilla_identidad.md`; `content/besorah/markos_4_palabra_tormenta_fidelidad.md`                                                   |
|  22 | `fruto`             | Fruto, permanencia y obediencia              | Formación             | `content/besorah/yojanan_15_vid_fruto_amor_discipulado.md`; `content/besorah/colosenses_3_vida_renovada_amor_y_servicio.md`                                             |
|  23 | `poda`              | Poda, corrección y permanencia               | Madurez               | `content/besorah/yojanan_15_vid_labrador_poda_permanecer.md`; `content/besorah/hebreos_12_disciplina_santidad_y_monte_tziyon.md`                                        |
|  24 | `omer-primicias`    | Omer, primicias y resurrección               | Fiestas               | `content/temas/omer_reshit_primicia_resurreccion.md`; `content/temas/resurreccion_primer_dia_y_omer.md`                                                                 |
|  25 | `pesaj`             | Pésaj, memoria, liberación y mesa            | Fiestas               | `content/temas/pesaj_memoria_liberacion_y_mesa.md`; `content/besorah/yojanan_13_pesaj_seuda_lavado_pies.md`                                                             |
|  26 | `shabat`            | Shabat, reposo y límites de la obra          | Fiestas               | `content/temas/shabat.md`; `content/besorah/yojanan_5_bet_jesda_shabat.md`                                                                                              |
|  27 | `sukot`             | Sucot, morada, cosecha y gozo                | Fiestas               | `content/temas/sukot_habitar_gozo_y_memoria.md`; `content/besorah/yojanan_7_sucot_agua_y_discernimiento.md`                                                             |
|  28 | `shavuot`           | Shavuot, palabra, promesa y comunidad        | Fiestas               | `content/temas/shavuot_convocacion_primicias_y_promesa.md`; `content/temas/shavuot_en_mashiaj_promesa_y_era_mesianica.md`                                               |
|  29 | `janukah`           | Janukah, dedicación y memoria                | Fiestas               | `content/temas/janukah.md`; `content/besorah/yojanan_10_janukah_senales_mesias.md`                                                                                      |
|  30 | `nombre`            | Nombre, autoridad y salvación                | Identidad             | `content/temas/nombre_de_יהוה_escritura_pronunciacion_y_fidelidad.md`; `content/temas/nombre_salvacion_sacerdocio_mesias.md`; `content/besorah/yojanan_14_abba_menajem_nombre.md` |
|  31 | `shema`             | Escuchar, amar y guardar                     | Obediencia            | `content/temas/cantos_hebreos_shema_memoria_y_discernimiento.md`; `content/besorah/markos_12_shema_senor_david_vida_entregada.md`                                       |
|  32 | `santidad`          | Santidad como orden y práctica               | Formación             | `content/temas/corazon_renovado_orden_santidad.md`; `content/besorah/efesios_5_amor_luz_y_sabiduria.md`                                                                 |
|  33 | `justicia`          | Justicia, misericordia y fidelidad           | Ética                 | `content/tanaj/micah_6_justicia_bondad_y_caminar.md`; `content/besorah/romanos_12_culto_vivo_dones_amor_practico.md`                                                    |
|  34 | `emunah`            | Emunah: don de Elohim, el único neeman       | Discipulado           | `content/besorah/yojanan_oracion_dos_tronos_emunah.md`; `content/tanaj/devarim_7_recordar_pacto_y_dependencia.md`; `content/tanaj/devarim_32_haazinu_roca_fidelidad.md` |
|  35 | `arrepentimiento`   | Volver, escuchar y escoger vida              | Retorno               | `content/tanaj/devarim_30_retornar_corazon_y_escoger_vida.md`; `content/besorah/apocalipsis_9_revelacion_trompetas_ay_y_llamado.md`                                     |
|  36 | `testimonio`        | Testimonio, palabra y perseverancia          | Misión                | `content/besorah/apocalipsis_1_revelacion_mensaje_testimonio_y_esperanza.md`; `content/besorah/yojanan_1_testigo_cordero.md`                                            |
|  37 | `discernimiento`    | Probar, distinguir y permanecer en la cabeza | Sabiduría             | `content/besorah/colosenses_2_plenitud_discernimiento_y_cabeza.md`; `content/besorah/apocalipsis_13_revelacion_bestias_discernimiento_y_perseverancia.md`               |
|  38 | `idolatria`         | Idolatría, imagen y lealtad                  | Advertencia           | `content/temas/neo-idolatria_origen_deseo_profanacion_y_babel.md`; `content/tanaj/tehilim_115_nombre_idolatria_y_confianza.md`; `content/besorah/apocalipsis_13_revelacion_bestias_discernimiento_y_perseverancia.md` |
|  39 | `babilonia`         | Seducción, poder y juicio                    | Discernimiento        | `content/besorah/apocalipsis_17_revelacion_babilonia_juicio_y_discernimiento.md`; `content/besorah/apocalipsis_22_revelacion_agua_vida_y_esperanza.md`                  |
|  40 | `bestias`           | Poder, engaño y perseverancia                | Apocalíptica          | `content/besorah/apocalipsis_13_revelacion_bestias_discernimiento_y_perseverancia.md`; `content/besorah/apocalipsis_17_revelacion_babilonia_juicio_y_discernimiento.md` |
|  41 | `remanente`         | Sello, preservación y fidelidad              | Esperanza             | `content/besorah/apocalipsis_7_revelacion_sello_siervos_y_multitud.md`; `content/besorah/apocalipsis_12_revelacion_mujer_hijo_y_conflicto.md`                           |
|  42 | `trono`             | Trono, adoración y autoridad                 | Reino                 | `content/besorah/apocalipsis_4_trono_redencion_y_adoracion.md`; `content/besorah/yojanan_17_gloria_autoridad_y_vida.md`                                                 |
|  43 | `santuario`         | Santuario, presencia y testimonio            | Presencia             | `content/tanaj/shemot_33_34_santuario_presencia_y_santidad.md`; `content/besorah/apocalipsis_15_revelacion_copas_ira_y_justicia.md`                                     |
|  44 | `sacerdocio`        | Servicio, mediación y acercamiento           | Servicio              | `content/temas/nombre_salvacion_sacerdocio_mesias.md`; `content/besorah/hebreos_7_melquisedec_sacerdocio_y_perfeccion.md`                                               |
|  45 | `oracion`           | Oración, vigilancia y confianza              | Comunión              | `content/besorah/yojanan_oracion_dos_tronos_emunah.md`; `content/besorah/efesios_6_firmeza_oracion_y_servicio.md`                                                       |
|  46 | `camino`            | Camino, seguimiento y retorno                | Discipulado           | `content/besorah/yojanan_12_camino_hora_luz_palabra.md`; `content/besorah/yojanan_14_moradas_camino_retorno.md`                                                         |
|  47 | `madero`            | Entrega, juicio y testimonio                 | Redención             | `content/besorah/yojanan_19_madero_costado_y_testimonio.md`; `content/besorah/markos_15_juicio_cruz_velo_confesion.md`                                                  |
|  48 | `resurreccion`      | Resurrección, vida y envío                   | Esperanza             | `content/besorah/yojanan_11_eleazar_resurreccion_vida.md`; `content/besorah/markos_16_resurreccion_envio_y_testimonio.md`                                               |
|  49 | `nueva-creacion`    | Nueva humanidad, vida renovada y esperanza   | Transformación        | `content/besorah/colosenses_3_vida_renovada_amor_y_servicio.md`; `content/besorah/romanos_8_vida_en_el_Ruaj_filiacion_sufrimiento_esperanza.md`                         |
|  50 | `permanecer`        | Permanecer en la palabra y dar fruto         | Perseverancia         | `content/besorah/yojanan_8_permanecer_en_la_palabra_y_ser_libres.md`; `content/besorah/yojanan_15_vid_fruto_amor_discipulado.md`                                        |

## Forma propuesta del card

```text
Concepto
Tesis breve

2–4 párrafos de explicación source-grounded.

Conexiones
- Versículos: referencias y texto/index link
- Notas: notas relacionadas
- Conceptos relacionados: otros cards

Alcance y cautelas
- Qué afirma la nota
- Qué se presenta como propuesta
- Qué queda pendiente de verificar
```

## Siguiente iteración

1. Revisar con Joni los cards reescritos, especialmente Abá, Ben-Hadam, Torah, pueblo, Ruaj, trono y nueva creación.
2. Decidir si neo-idolatría, Menájem y «dos tronos» merecen nodos propios o deben seguir atravesando otros cards.
3. Añadir versículos principales a cada card y relaciones entre conceptos.
4. Confirmar el contrato de datos para que una conexión pueda apuntar tanto a un versículo como a una nota.
5. Mantener cada card independiente de la UI: el contenido debe poder renderizarse como tooltip, drawer o página dedicada.
