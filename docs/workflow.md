# Quy tr├¼nh ph├ít triß╗ân (Development Workflow)

T├ái liß╗çu n├áy m├┤ tß║ú c├ích tß╗ò chß╗⌐c repository v├á c├ích c├íc thay ─æß╗òi tß╗½ nh├ính thiß║┐t kß║┐ (design branches) ─æ╞░ß╗úc ─æ╞░a v├áo nh├ính `main` ß╗òn ─æß╗ïnh.

## 1. M├┤ h├¼nh nh├ính (Branch Model)

Repository tu├ón theo m├┤ h├¼nh kiß╗âu **GitFlow** ─æ╞░ß╗úc ─æiß╗üu chß╗ënh cho ph├╣ hß╗úp vß╗¢i thiß║┐t kß║┐ phß║ºn cß╗⌐ng:

```text
main (ß╗òn ─æß╗ïnh, sß║╡n s├áng ph├ít h├ánh)
  Γû▓ merge sau khi ─æ├ính gi├í
develop (t├¡ch hß╗úp + th╞░ viß╗çn d├╣ng chung)
  Γû▓ merge qua pull request
  Γö£ΓöÇΓöÇ design/one-board     (One_Board_Design)
  ΓööΓöÇΓöÇ design/split-board   (Split_Board_Design)
```

| Nh├ính | Mß╗Ñc ─æ├¡ch | Nß╗Öi dung |
|---|---|---|
| `main` | Trß║íng th├íi ß╗òn ─æß╗ïnh, sß║╡n s├áng ph├ít h├ánh | Chß╗ë c├│ khung dß╗▒ ├ín: `README.md`, `LICENSE`, `.gitignore`, `Docs/` |
| `develop` | ─Éiß╗âm t├¡ch hß╗úp v├á t├ái sß║ún d├╣ng chung | Khung dß╗▒ ├ín + `Hardware/libraries/` (symbol, footprint, m├┤ h├¼nh 3D) |
| `design/one-board` | Ph├ít triß╗ân thiß║┐t kß║┐ mß╗Öt board | `Hardware/One_Board_Design/` + `Hardware/libraries/` |
| `design/split-board` | Ph├ít triß╗ân thiß║┐t kß║┐ t├ích board | `Hardware/Split_Board_Design/` + `Hardware/libraries/` |

## 2. Vai tr├▓ cß╗ºa tß╗½ng nh├ính

### `main`

- Chß╗ë chß╗⌐a nhß╗»ng nß╗Öi dung ─æ╞░ß╗úc coi l├á **ß╗òn ─æß╗ïnh v├á sß║╡n s├áng ph├ít h├ánh**.
- Trong giai ─æoß║ín prototype, kh├┤ng c├│ thiß║┐t kß║┐ board n├áo nß║▒m tr├¬n `main`.
- Mß╗Öt thiß║┐t kß║┐ board chß╗ë ─æ╞░ß╗úc ─æ╞░a l├¬n `main` sau khi ─æ├ú ─æ╞░ß╗úc ─æ├ính gi├í v├á x├íc nhß║¡n, ─æß╗ông thß╗¥i ─æ├ú ─æ╞░ß╗úc merge v├áo `develop` v├á ─æ╞░ß╗úc ph├¬ duyß╗çt.

### `develop`

- L├á **nh├ính t├¡ch hß╗úp**: mß╗ìi thay ─æß╗òi ─æ├ú ─æ╞░ß╗úc ─æ├ính gi├í ─æß╗üu ─æ╞░ß╗úc merge v├áo ─æ├óy tr╞░ß╗¢c khi ─æß║┐n `main`.
- L╞░u trß╗» **th╞░ viß╗çn d├╣ng chung** (`Hardware/libraries/`) ΓÇö nguß╗ôn duy nhß║Ñt (single source of truth) cho symbol, footprint v├á m├┤ h├¼nh 3D ─æ╞░ß╗úc sß╗¡ dß╗Ñng bß╗ƒi mß╗ìi thiß║┐t kß║┐ board.
- C├íc thay ─æß╗òi th╞░ viß╗çn ─æ╞░ß╗úc thß╗▒c hiß╗çn tr├¬n `develop` (hoß║╖c qua mß╗Öt nh├ính ngß║»n hß║ín ─æ╞░ß╗úc merge v├áo `develop`).

### C├íc nh├ính `design/*`

- Mß╗ùi thiß║┐t kß║┐ board ─æ╞░ß╗úc ph├ít triß╗ân tr├¬n **nh├ính ri├¬ng cß╗ºa n├│**.
- `design/one-board`   ΓåÆ thiß║┐t kß║┐ mß╗Öt board (One_Board_Design).
- `design/split-board` ΓåÆ thiß║┐t kß║┐ board t├ích ─æiß╗üu khiß╗ân/r╞í-le (Split_Board_Design).
- C├íc nh├ính n├áy **merge `develop` ─æß╗ïnh kß╗│** ─æß╗â nhß║¡n th╞░ viß╗çn d├╣ng chung v├á c├íc cß║¡p nhß║¡t khung dß╗▒ ├ín mß╗¢i nhß║Ñt.

## 3. Luß╗ông thay ─æß╗òi (Change Flow)

```mermaid
flowchart LR
    OB["design/one-board"] -->|PR| DEV["develop"]
    SB["design/split-board"] -->|PR| DEV
    LIB["thay ─æß╗òi th╞░ viß╗çn"] --> DEV
    DEV -->|─æ├ính gi├í| DEV
    DEV -->|PR / merge ─æ╞░ß╗úc duyß╗çt| MAIN["main"]
```

### 3.1 L├ám viß╗çc tr├¬n mß╗Öt thiß║┐t kß║┐ board

1. Chuyß╗ân sang nh├ính thiß║┐t kß║┐ t╞░╞íng ß╗⌐ng:
   ```sh
   git checkout design/one-board      # hoß║╖c design/split-board
   ```
2. K├⌐o c├íc t├ái sß║ún d├╣ng chung mß╗¢i nhß║Ñt tß╗½ `develop`:
   ```sh
   git fetch origin
   git merge origin/develop
   ```
3. Thß╗▒c hiß╗çn c├íc thay ─æß╗òi schematic / PCB.
4. Chß║íy ERC v├á DRC, ghi lß║íi bß║▒ng chß╗⌐ng ─æ├ính gi├í.
5. Commit vß╗¢i th├┤ng ─æiß╗çp m├┤ tß║ú r├╡ r├áng (xem [Quy ╞░ß╗¢c commit](#6-quy-╞░ß╗¢c-commit)).
6. Push nh├ính:
   ```sh
   git push origin design/one-board
   ```
7. Mß╗ƒ pull request v├áo `develop`.

### 3.2 Thay ─æß╗òi th╞░ viß╗çn d├╣ng chung

Th╞░ viß╗çn d├╣ng chung (symbol, footprint, m├┤ h├¼nh 3D) nß║▒m tr├¬n `develop`:

1. Tß║ío mß╗Öt nh├ính ngß║»n hß║ín tß╗½ `develop` (hoß║╖c l├ám viß╗çc trß╗▒c tiß║┐p tr├¬n `develop` cho c├íc thay ─æß╗òi nhß╗Å):
   ```sh
   git checkout develop
   git checkout -b fix/library-xyz
   ```
2. Chß╗ënh sß╗¡a c├íc file th╞░ viß╗çn trong `Hardware/libraries/`.
3. Commit, push, v├á mß╗ƒ pull request trß╗ƒ lß║íi v├áo `develop`.
4. Sau khi thay ─æß╗òi th╞░ viß╗çn ─æ╞░ß╗úc merge v├áo `develop`, mß╗ùi nh├ính thiß║┐t kß║┐ merge `develop` ─æß╗â nhß║¡n bß║ún cß║¡p nhß║¡t.

### 3.3 Ph├ít h├ánh l├¬n `main`

1. ─Éß║úm bß║úo mß╗ìi thay ─æß╗òi board ─æ├ú ─æ╞░ß╗úc merge v├áo `develop` v├á ─æ├ú ─æ╞░ß╗úc ─æ├ính gi├í.
2. Khi trß║íng th├íi t├¡ch hß╗úp ─æ╞░ß╗úc coi l├á ß╗òn ─æß╗ïnh:
   ```sh
   git checkout main
   git merge develop
   git push origin main
   ```
   hoß║╖c mß╗ƒ pull request tß╗½ `develop` v├áo `main`.
3. Tß║ío tag cho bß║ún ph├ít h├ánh nß║┐u cß║ºn:
   ```sh
   git tag -a v0.1.0 -m "First prototype baseline"
   git push origin v0.1.0
   ```

## 4. Cß║Ñu tr├║c repository hiß╗çn tß║íi

```text
robot_charge_controller/
Γö£ΓöÇΓöÇ README.md                 # Tß╗òng quan dß╗▒ ├ín
Γö£ΓöÇΓöÇ LICENSE                   # Giß║Ñy ph├⌐p dß╗▒ ├ín
Γö£ΓöÇΓöÇ .gitignore
Γö£ΓöÇΓöÇ docs/                     # Y├¬u cß║ºu, kiß║┐n tr├║c, thiß║┐t kß║┐, t├¡nh to├ín, ─æ├ính gi├í, kiß╗âm chß╗⌐ng
Γöé   Γö£ΓöÇΓöÇ 01-requirements/
Γöé   Γö£ΓöÇΓöÇ 02-architecture/
Γöé   Γö£ΓöÇΓöÇ 03-design/
Γöé   Γö£ΓöÇΓöÇ 04-calculations/
Γöé   Γö£ΓöÇΓöÇ 05-reviews/
Γöé   Γö£ΓöÇΓöÇ 06-verification/
Γöé   Γö£ΓöÇΓöÇ decisions/
Γöé   ΓööΓöÇΓöÇ workflow.md           # T├ái liß╗çu n├áy
Γö£ΓöÇΓöÇ hardware/                 # Thiß║┐t kß║┐ phß║ºn cß╗⌐ng
Γöé   Γö£ΓöÇΓöÇ libraries/            # D├╣ng chung: symbol, footprint, m├┤ h├¼nh 3D (tr├¬n develop)
Γöé   ΓööΓöÇΓöÇ templates/            # Template KiCad d├╣ng chung
Γö£ΓöÇΓöÇ firmware/                 # Firmware ESP32 (include, src, lib, test)
Γö£ΓöÇΓöÇ simulation/               # M├┤ phß╗Ång SPICE
Γö£ΓöÇΓöÇ components/               # BOM, linh kiß╗çn thay thß║┐, datasheet
Γö£ΓöÇΓöÇ manufacturing/            # Ghi ch├║ chß║┐ tß║ío, bß╗Ö hß╗ô s╞í ph├ít h├ánh
Γö£ΓöÇΓöÇ test/                     # ─Éo l╞░ß╗¥ng, b├ío c├ío kiß╗âm tra phß║ºn cß╗⌐ng
ΓööΓöÇΓöÇ tools/                    # Script xuß║Ñt, kiß╗âm tra, tß╗▒ ─æß╗Öng h├│a
```

> [!NOTE]
> `hardware/libraries/` ─æ╞░ß╗úc duy tr├¼ tr├¬n nh├ính `develop` ΓÇö nguß╗ôn duy nhß║Ñt cho symbol,
> footprint v├á m├┤ h├¼nh 3D d├╣ng chung. C├íc thiß║┐t kß║┐ board cß╗Ñ thß╗â
> (`One_Board_Design`, `Split_Board_Design`) ─æ╞░ß╗úc ph├ít triß╗ân tr├¬n c├íc nh├ính
> `design/one-board` v├á `design/split-board`.

## 5. Cß╗òng kiß╗âm tra chß║Ñt l╞░ß╗úng (Quality Gates)

Tr╞░ß╗¢c khi mß╗Öt nh├ính thiß║┐t kß║┐ ─æ╞░ß╗úc merge v├áo `develop`, c├íc kiß╗âm tra sau phß║úi ─æß║ít v├á ─æ╞░ß╗úc ghi lß║íi:

| Cß╗òng kiß╗âm tra | C├┤ng cß╗Ñ | Y├¬u cß║ºu |
|---|---|---|
| Kiß╗âm tra quy tß║»c ─æiß╗çn (ERC) | KiCad `kicad-cli sch erc` | Kh├┤ng c├│ lß╗ùi; c├íc cß║únh b├ío ─æ├ú ─æ╞░ß╗úc xem x├⌐t |
| Kiß╗âm tra quy tß║»c thiß║┐t kß║┐ (DRC) | KiCad `kicad-cli pcb drc` | Kh├┤ng c├│ vi phß║ím ch╞░a ─æ╞░ß╗úc ph├¬ duyß╗çt |
| ─Éß╗Ö ph├ón giß║úi th╞░ viß╗çn | KiCad | Kh├┤ng thiß║┐u symbol, footprint hoß║╖c m├┤ h├¼nh 3D |
| ─É├ính gi├í thiß║┐t kß║┐ | ─É├ính gi├í kß╗╣ thuß║¡t | ─É├ú ─æ╞░ß╗úc ─æ├ính gi├í v├á ph├¬ duyß╗çt |
| Kiß╗âm tra sß║ún xuß║Ñt | KiCad / nh├á m├íy | Chß╗ë tr╞░ß╗¢c khi ph├ít h├ánh chß║┐ tß║ío |

## 6. Quy ╞░ß╗¢c commit

Th├┤ng ─æiß╗çp commit tu├ón theo **phong c├ích ngß╗» ngh─⌐a (semantic style)** cß╗ºa repository:

- `feat(hardware): ...` ΓÇö t├¡nh n─âng hoß║╖c khß║ú n─âng mß╗¢i
- `fix(hardware): ...` ΓÇö sß╗¡a lß╗ùi
- `refactor(hardware): ...` ΓÇö t├íi cß║Ñu tr├║c kh├┤ng thay ─æß╗òi h├ánh vi
- `chore: ...` ΓÇö bß║úo tr├¼, dß╗ìn dß║╣p, thay ─æß╗òi kh├┤ng chß╗⌐c n─âng
- `docs: ...` ΓÇö chß╗ë t├ái liß╗çu

V├¡ dß╗Ñ vß╗ü scope: `hardware`, `firmware`, `docs`, `libraries`.

V├¡ dß╗Ñ:

```sh
git commit -m "fix(hardware): correct 3D model paths in shared footprints"
```

## 7. Vß╗ç sinh nh├ính (Branch Hygiene)

- X├│a mß╗Öt nh├ính thiß║┐t kß║┐ sau khi n├│ ─æ├ú ─æ╞░ß╗úc merge v├á kh├┤ng c├▓n cß║ºn thiß║┐t:
  ```sh
  git push origin --delete design/one-board
  git branch -d design/one-board
  ```
- Giß╗» `main` sß║ích: n├│ kh├┤ng bao giß╗¥ ─æ╞░ß╗úc chß╗⌐a thiß║┐t kß║┐ ─æang triß╗ân khai dß╗ƒ dang.
- Rebase hoß║╖c merge `develop` v├áo c├íc nh├ính thiß║┐t kß║┐ th╞░ß╗¥ng xuy├¬n ─æß╗â giß║úm thiß╗âu xung ─æß╗Öt.
- Tß║ío tag cho c├íc mß╗æc quan trß╗ìng (baseline prototype, ─æiß╗âm kiß╗âm tra ─æ├ính gi├í, bß║ún ph├ít h├ánh).
