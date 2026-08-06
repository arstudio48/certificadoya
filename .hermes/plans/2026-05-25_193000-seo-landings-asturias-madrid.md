# Plan: Landing Pages Asturias & Madrid — SEO Local + CRO

> **Para Hermes:** Ejecutar con subagent-driven-development, una tarea por subagente.

## Asturias

### Objetivos
- Crear landing locales para Oviedo, Gijón, Avilés, Siero, Langreo, Mieres (ciudades)
- Crear 5 páginas transaccionales (precio, urgente, alquiler, venta, multa)
- Sección captación de técnicos Asturias
- Schema local, FAQ, CTA, WhatsApp

## Madrid

### Objetivos
- Crear 14 landing hiperlocales (distritos + municipios)
- Crear 6 páginas transaccionales
- Sección captación técnicos Madrid
- Schema, CRO, interlinking avanzado

## Prioridad de ejecución
1. Asturias primero (menos competitivo, más fácil posicionar)
2. Madrid después (más volumen pero requiere hiperlocal)

---

## ESTADO ACTUAL

### Ya existe:
- `certificado-energetico-madrid/index.html` — página general de Madrid (completa)
- `certificado-energetico-asturias/index.html` — página general de Asturias (completa)

### No existe:
- Landing de ciudades individuales (Oviedo, Gijón, etc.)
- Landing de distritos de Madrid
- Páginas transaccionales (precio, urgente, etc.)
- Secciones específicas de captación de técnicos por zona

---

## PARTE 1: ASTURIAS (6 landings ciudad + 5 transaccionales + 1 técnicos = 12 nuevos directorios)

### TASK 1.1: Crear estructura base para landing local (ciudad)
Crear script generador que dada una ciudad y datos, genere:
- `certificado-energetico-oviedo/index.html`
- `certificado-energetico-gijon/index.html`
- `certificado-energetico-aviles/index.html`
- `certificado-energetico-siero/index.html`
- `certificado-energetico-langreo/index.html`
- `certificado-energetico-mieres/index.html`

Cada landing debe tener:
- Title SEO localizado
- Meta description con ciudad y precio
- H1: "Certificado energético en [Ciudad]"
- Lead con precio desde
- Calculadora de presupuesto (misma que Madrid pero con precios Asturias: 40-65€)
- Schema LocalBusiness + FAQ + BreadcrumbList
- 5 FAQ locales específicas de la ciudad
- CTA band
- Tasa aviso autonómica (Asturias: https://www.asturias.es/...)
- CTA técnicos localizada
- Open Graph, Twitter cards
- CSS embebido (mismo que Madrid)

Precios base Asturias: piso 40-65€, unifamiliar 65-90€, local 50-75€

### TASK 1.2: Páginas transaccionales Asturias
- `certificado-energetico-precio-asturias/index.html`
- `certificado-energetico-urgente-asturias/index.html`
- `certificado-energetico-alquiler-asturias/index.html`
- `certificado-energetico-venta-vivienda-asturias/index.html`
- `multa-no-tener-certificado-energetico-asturias/index.html`

Cada una con contenido SEO único, schema, FAQ, CTA.

### TASK 1.3: Sección técnicos Asturias
- En cada landing de Asturias, añadir CTA "Trabaja como técnico en [Ciudad]"
- Crear sección específica en panel-tecnicos.html si no existe filtro por Asturias

---

## PARTE 2: MADRID (14 landings distrito + 6 transaccionales + 1 técnicos = 21 nuevos directorios)

### TASK 2.1: Landing hiperlocales Madrid
Mismo generador pero con precios Madrid (60-96€):
- `certificado-energetico-madrid-centro/`
- `certificado-energetico-chamberi/`
- `certificado-energetico-salamanca-madrid/`
- `certificado-energetico-retiro/`
- `certificado-energetico-chamartin/`
- `certificado-energetico-tetuan/`
- `certificado-energetico-mostoles/`
- `certificado-energetico-getafe/`
- `certificado-energetico-leganes/`
- `certificado-energetico-alcala-de-henares/`
- `certificado-energetico-alcorcon/`
- `certificado-energetico-fuenlabrada/`
- `certificado-energetico-pozuelo/`
- `certificado-energetico-alcobendas/`

Cada una con contenido ÚNICO (no copiar entre distritos), referencias locales reales.

### TASK 2.2: Páginas transaccionales Madrid
- `certificado-energetico-urgente-madrid/`
- `precio-certificado-energetico-madrid/`
- `certificado-energetico-barato-madrid/`
- `certificado-energetico-alquiler-madrid/`
- `certificado-energetico-venta-vivienda-madrid/`
- `certificado-energetico-mismo-dia-madrid/`

### TASK 2.3: Sección técnicos Madrid
- CTA específica en cada landing de Madrid
- Sección en panel-tecnicos.html

---

## PARTE 3: INTERLINKING & SITEMAP

### TASK 3.1: Actualizar sitemap.xml
Añadir todas las URLs nuevas (6+5+14+6 = 31 nuevas URLs aprox)

### TASK 3.2: Actualizar navegación
- En breadcrumbs de home, enlazar a Asturias y Madrid
- En cada landing, enlazar a las otras de la misma región
- En cada transaccional, enlazar a las landings de ciudad

### TASK 3.3: Google Business Profile
Recomendar crear GBP para cada distrito/zona

---

## CRONOGRAMA DE EJECUCIÓN

1. Crear script generador de landing local (reutilizable)
2. Generar 6 landings Asturias (Oviedo, Gijón, Avilés, Siero, Langreo, Mieres)
3. Generar 5 transaccionales Asturias
4. Verificar contenido único + schema + CRO
5. Generar 14 landings Madrid (distritos + municipios)
6. Generar 6 transaccionales Madrid
7. Secciones técnicos en todas
8. Sitemap + interlinking + deploy

---

## ESQUEMA DE ARCHIVOS

```
certificadoya/
├── certificado-energetico-oviedo/index.html
├── certificado-energetico-gijon/index.html
├── certificado-energetico-aviles/index.html
├── certificado-energetico-siero/index.html
├── certificado-energetico-langreo/index.html
├── certificado-energetico-mieres/index.html
├── certificado-energetico-precio-asturias/index.html
├── certificado-energetico-urgente-asturias/index.html
├── certificado-energetico-alquiler-asturias/index.html
├── certificado-energetico-venta-vivienda-asturias/index.html
├── multa-no-tener-certificado-energetico-asturias/index.html
├── certificado-energetico-madrid-centro/index.html
├── certificado-energetico-chamberi/index.html
├── certificado-energetico-salamanca-madrid/index.html
├── certificado-energetico-retiro/index.html
├── certificado-energetico-chamartin/index.html
├── certificado-energetico-tetuan/index.html
├── certificado-energetico-mostoles/index.html
├── certificado-energetico-getafe/index.html
├── certificado-energetico-leganes/index.html
├── certificado-energetico-alcala-de-henares/index.html
├── certificado-energetico-alcorcon/index.html
├── certificado-energetico-fuenlabrada/index.html
├── certificado-energetico-pozuelo/index.html
├── certificado-energetico-alcobendas/index.html
├── certificado-energetico-urgente-madrid/index.html
├── precio-certificado-energetico-madrid/index.html
├── certificado-energetico-barato-madrid/index.html
├── certificado-energetico-alquiler-madrid/index.html
├── certificado-energetico-venta-vivienda-madrid/index.html
├── certificado-energetico-mismo-dia-madrid/index.html
└── sitemap.xml (actualizado)
```

---

## TECNOLOGÍA
- HTML plano con CSS embebido (mismo estilo que Madrid)
- Schema JSON-LD embebido
- Sin frameworks
- Sin dependencias externas
- Script presupuesto inline
- Supabase para leads (mismo que ya funciona)

## VERIFICACIÓN
- Cada página: curl + validar title, meta description, H1, schema, CTA
- No duplicados entre ciudades
- Sitemap XML válido
- Breadcrumbs correctos
- Enlaces internos funcionales
