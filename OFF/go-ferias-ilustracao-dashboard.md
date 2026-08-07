# Ilustração do banner do Dashboard

Como foi feita a cena "rede sob palmeiras" que aparece no banner de boas-vindas
do Dashboard (`#/dashboard`), em `index.html`.

## Resumo

Não é uma imagem importada (PNG/JPG) nem um ícone de biblioteca — é um único
**SVG desenhado à mão, inline no HTML**, animado com CSS e controlado por
pouco JS para alternar entre sol e lua conforme o horário.

- Markup do SVG: `index.html`, a partir da linha **1953** (`<svg id="dxArtPraia">`)
- CSS da cena: a partir da linha **1097** (`/* cena animada do banner */`)
- Lógica dia/noite: por volta da linha **5012-5021**

## Estrutura do SVG

```
<svg id="dxArtPraia" viewBox="0 0 360 240">
  <defs>...gradientes, clipPaths, símbolo da folha...</defs>
  <g id="dxSun">...</g>       sol (visível de dia)
  <g id="dxMoon">...</g>      lua (visível à noite)
  <g class="dx-cloud">...</g> nuvens
  <g mask="...">...</g>       areia (com fade nas bordas)
  <g>...palmeira esquerda...</g>
  <g>...palmeira direita...</g>
  <g class="dx-hammock">...</g>  rede + boneco relaxando
</svg>
```

Tudo empilhado na ordem de profundidade: céu → nuvens → areia → troncos →
copas → rede → boneco.

## Técnicas usadas

- **Gradientes em `<defs>`** (`dxSand`, `dxTrunk`, `dxLeaf`, `dxSunG`) dão
  volume à areia, ao tronco, às folhas e ao sol sem precisar de imagem raster.
- **Reuso via `<symbol>` + `<use>`**: a folha da palmeira (`#dxFrond`) é
  desenhada uma única vez e repetida com `rotate()`/`scale()` diferentes para
  montar a copa inteira — e espelhada com `scale(-1,1)` para a palmeira do
  lado direito.
- **`clipPath`** recorta as linhas de textura da casca dentro do contorno
  curvo de cada tronco (`dxTrunkClipL` / `dxTrunkClipR`).
- **`mask` com gradiente linear** (`dxGMaskP`) esmaece a areia na borda,
  fundindo com o fundo do banner em vez de terminar num corte seco.
- **Boneco na rede**: feito só com `path`/`circle`/`ellipse` simples — chapéu
  de palha, camiseta, braço sobre a barriga, perna esticada. Nenhum ícone
  externo, tudo vetor desenhado à mão.
- **Camada "lábio" da rede** por cima do boneco: um segundo `path` do mesmo
  formato da rede é redesenhado por cima das pernas/torso, dando a impressão
  de que o corpo está "dentro" do tecido.

## Animação

```css
.dx-hammock{
  transform-box: fill-box;
  transform-origin: 50% 4%;
  animation: dxSway 4.8s ease-in-out infinite;
}
```

Só CSS — o grupo inteiro da rede (cordas + tecido + boneco) balança em torno
do ponto de fixação no topo, sem nenhum JS de animação.

## Dia / noite dinâmico

Em JS, o horário atual decide o período (`manha` / `tarde` / `noite`), que:

1. troca a classe do banner (`heroEl.classList.add(periodo)`) — afeta a cor
   de fundo via CSS;
2. alterna `display` entre `#dxSun` e `#dxMoon`, mostrando um ou outro.

A lua tem sua própria composição SVG (crescente + estrelinhas), separada do
sol, então nada é reaproveitado entre os dois — cada um é seu próprio grupo
completo.

## Por que assim, e não uma imagem

- Zero assets externos para carregar/hospedar.
- Escala perfeitamente em qualquer resolução (é vetor).
- Cores herdam fácil da paleta do app via CSS/gradientes.
- Dá para alternar sol/lua e animar sem precisar de sprites ou vídeo.
