# Fix npm registry 403

Se `npm install`/`npm ci` fallisce con `403` è quasi sempre un registry non ufficiale o un proxy che blocca il traffico.

## Soluzioni rapide
1) **Forza il registry ufficiale**
```bash
npm config set registry https://registry.npmjs.org/
```
Per pnpm:
```bash
pnpm config set registry https://registry.npmjs.org/
```
Controllo rapido:
```bash
pnpm config get registry
```
Oppure crea un `.npmrc` con:
```
registry=https://registry.npmjs.org/
```

2) **Rimuovi override aziendali/proxy**
- Controlla `~/.npmrc`, `.npmrc` nel repo, variabili `NPM_CONFIG_REGISTRY`.
- Elimina registry custom non autorizzati.

3) **Fallback hotspot / rete alternativa**
- Se sei su rete aziendale/VPN, prova un hotspot personale o una rete non filtrata.

4) **CI/Cloudflare Pages**
Imposta la variabile d’ambiente:
```
NPM_CONFIG_REGISTRY=https://registry.npmjs.org/
```

## Checklist diagnostica
```bash
npm config get registry
node -v
npm -v
```
