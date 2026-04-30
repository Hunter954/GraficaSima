# Gráfica Vitrine - Flask + PostgreSQL

MVP de site vitrine para gráfica, inspirado no layout enviado, com identidade azul `#005ba9`. O foco inicial é apresentar produtos e gerar contatos pelo WhatsApp, mantendo a estrutura preparada para e-commerce futuro.

## Recursos incluídos

- Home com banner, categorias, destaques, diferenciais, CTA de WhatsApp e footer completo.
- Catálogo com busca, filtro por categoria, ordenação e paginação.
- Página de produto com imagem, galeria, opções, produtos relacionados e botão de orçamento via WhatsApp.
- Páginas institucionais: sobre, contato, privacidade, termos e orientações de produção.
- Painel admin com login protegido, dashboard, CRUD de categorias, CRUD de produtos e configurações do site.
- Upload de imagens com validação de extensão, tamanho e sanitização do nome do arquivo.
- SQLAlchemy, Flask-Migrate, PostgreSQL e `.env`.
- Campos preparados para e-commerce futuro: SKU, preço, preço promocional, estoque e permitir compra online.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env`. Para testar rápido com SQLite, deixe `DATABASE_URL` vazio ou remova essa linha.

```bash
flask --app wsgi db init
flask --app wsgi db migrate -m "initial"
flask --app wsgi db upgrade
flask --app wsgi seed
flask --app wsgi run
```

Acesse:

- Site: `http://127.0.0.1:5000`
- Admin: `http://127.0.0.1:5000/admin/login`

O comando `flask --app wsgi seed` cria dados iniciais e um admin usando `ADMIN_EMAIL` e `ADMIN_PASSWORD` do `.env`.

## Deploy no Railway

1. Suba este projeto no GitHub.
2. Crie um projeto no Railway a partir do repositório.
3. Adicione um banco PostgreSQL no Railway.
4. Configure as variáveis:
   - `SECRET_KEY`
   - `DATABASE_URL` (Railway normalmente injeta automaticamente)
   - `ADMIN_EMAIL`
   - `ADMIN_PASSWORD`
   - `SITE_URL`
   - `UPLOAD_FOLDER=/app/app/static/uploads`
5. Configure um volume persistente no Railway apontando para `/app/app/static/uploads`.
6. Após o deploy, execute no Railway shell:

```bash
flask --app wsgi db upgrade
flask --app wsgi seed
```

## Observação sobre uploads

Em produção, as imagens ficam no caminho definido por `UPLOAD_FOLDER`. Em Railway, use volume persistente para não perder arquivos entre deploys.

## Próxima fase planejada

Carrinho, checkout, Mercado Pago, área do cliente, pedidos, frete, CEP, cupons e pagamento online ficaram fora desta fase, mas os modelos já têm campos-base para evoluir.
