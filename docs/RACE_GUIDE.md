# คู่มือการแข่งขัน UmaDnDBot

## Introduction

นี่คือเกมแข่งม้าแบบผลัดเทิร์นใน Discord ผู้เล่นสะสม `Score` ด้วยการ Run ให้มากที่สุดเมื่อสนามจบ ผู้ที่มี Score สูงสุดชนะการแข่งขัน

คู่มือนี้แบ่งเป็นสองเส้นทางอ่าน:

- **เริ่มเล่นทันที:** อ่าน Introduction, Quick Start และ Race Flow ตามลำดับ
- **ศึกษาระบบ:** อ่าน Before Race, Turn Actions, Race Mechanics, Strategy Guide, Dictionary และ Formula Reference เมื่อต้องการรายละเอียดเพิ่ม

ชื่อระบบ เช่น Status, Skill, Zone, Stamina, Gold/White, Draft และ Block จะอธิบายเต็มรูปแบบเพียงครั้งเดียวใน **Race Mechanics** เพื่อลดข้อมูลซ้ำ ส่วนอื่นจะบอกเฉพาะสิ่งที่ต้องทำและลิงก์กลับไปยังหัวข้อนั้น

## Quick Start

1. ใช้ `/game create` แล้วเลือกสนาม หรือรอเข้าห้องที่มีผู้สร้างไว้แล้ว
2. กด **Join** และเลือกสไตล์การวิ่งที่ต้องการ
3. ผู้สร้างกด **Start** เมื่อทุกคนพร้อม
4. ในทุกเทิร์น ใช้ `/game run` หนึ่งครั้ง แล้วดูผลการวิ่งของตน
5. เมื่อทุกคน Run แล้ว ให้เลือกเลนของเทิร์นถัดไปถ้าต้องการ และกด **ยืนยัน** ในข้อความสรุปเทิร์น
6. ทำซ้ำจนจบสนาม ผู้มี Score สูงสุดเป็นผู้ชนะ

ในครั้งแรก ไม่จำเป็นต้องใช้ Skill, Zone, Rush, Block หรือ Reroll ก่อน รู้เพียงว่า Score มากกว่าคือชนะก็เริ่มแข่งได้แล้ว

## Before Race

### สร้างและเข้าห้อง

- `/game create` เปิดเมนูเลือกสนาม; ผู้สร้างเป็นเจ้าของห้อง
- ผู้เล่นกด **Join** ใน Lobby แล้วเลือก `Front`, `Pace`, `Late` หรือ `End`
- เจ้าของห้องกด **Start** เพื่อเริ่มการแข่งขัน
- `/game add_mob` และ `/game add_rookies` ใช้เพิ่มคู่แข่งบอทก่อนเริ่มได้

สนามระบุจำนวนเทิร์น พื้นผิว ระยะ และลักษณะเส้นทางไว้แล้ว ค่าพวกนี้มีผลกับ Aptitude และผลของเส้นทาง ดูรายละเอียดที่ [Race Mechanics — Status และ Aptitude](#status-และ-aptitude) และ [Formula Reference](#formula-reference)

### เตรียมโปรไฟล์

Stat และ Aptitude ในโปรไฟล์จะถูก snapshot ตอนเริ่มแข่ง จึงควรจัดสรรให้เสร็จก่อนกด Start โดยเฉพาะสไตล์ ระยะ และพื้นผิวที่ตรงกับสนาม

หากจะใช้ระบบเสริม ให้กำหนด Skill ในช่องสกิลและตั้งค่า Zone ก่อนแข่ง รายละเอียดอยู่ที่ [Race Mechanics — Skill](#skill) และ [Race Mechanics — Zone](#zone)

## Race Flow

### ลำดับการแข่งขัน

1. **Lobby:** เลือกสนาม เข้าร่วม และเลือกสไตล์
2. **เริ่มแข่ง:** ระบบสุ่มลำดับออกตัว กำหนดเลนเริ่มต้น และเติม Stamina/Wit สำหรับการแข่งขัน
3. **แต่ละเทิร์น:** ผู้เล่นใช้ `/game run` หนึ่งครั้ง ระบบคำนวณผลจากสถานะเมื่อเริ่มเทิร์นเดียวกัน จึงไม่ต้องกังวลว่าใครกดก่อน
4. **สรุปเทิร์น:** เมื่อทุกคน Run แล้ว จะปรากฏอันดับปัจจุบัน ผู้เล่นอาจเลือกเลนเทิร์นถัดไป และใช้ Rush หรือ Block ก่อนยืนยัน
5. **ยืนยัน:** ทุกคนกด **ยืนยัน** เพื่อไปเทิร์นถัดไป; หากหมดเวลาแต่ทุกคน Run แล้ว ระบบไปต่อได้
6. **จบสนาม:** หลังเทิร์นสุดท้าย ระบบเรียง Score และประกาศผล

### สิ่งที่ผู้เล่นใหม่ต้องทำในหนึ่งเทิร์น

ใช้ `/game run` แล้วกด **ยืนยัน** หลังผลรวมเทิร์นปรากฏเท่านั้น การเปลี่ยนเลน, Skill, Zone, Rush, Block และ Reroll เป็นทางเลือก ไม่ต้องใช้เพื่อเริ่มเล่น

ผล Run แสดงสี White/Gold, กติกาเต๋า, โบนัส, Score ที่ได้ และ Stamina คงเหลือ ความหมายเชิงลึกของสิ่งเหล่านี้อยู่ที่ [Race Mechanics](#race-mechanics)

## Turn Actions

หัวข้อนี้เป็นรายการการกระทำเท่านั้น; กติกา ผล และข้อจำกัดของแต่ละระบบอยู่ที่ [Race Mechanics](#race-mechanics)

| ช่วงเวลา | การกระทำ | วิธีใช้ |
| --- | --- | --- |
| ก่อน Run | ใช้ Skill | `/game skill` หรือปุ่ม Skill ในหน้าการแข่ง |
| ก่อน Run | ใช้ Zone | ปุ่ม Zone; ใช้ได้หนึ่งครั้งต่อการแข่งขัน |
| Run | วิ่ง | `/game run` หนึ่งครั้งต่อเทิร์น |
| หลัง Run | Reroll | ปุ่ม Reroll ที่แสดงพร้อมผล Run เมื่อยังใช้ได้ |
| สรุปเทิร์น | เปลี่ยนเลน | `/game lane target_lane:1-6`; มีผลเทิร์นถัดไป |
| สรุปเทิร์น | Rush / Block | ปุ่ม Rush หรือ Block ในข้อความยืนยัน |
| สรุปเทิร์น | ไปต่อ | กด **ยืนยัน** |

## Race Mechanics

### Status และ Aptitude

Stat หลักในโปรไฟล์คือ Speed, Stamina, Power, Gut และ Wit

- **Speed:** เพิ่มโบนัสผล Run และกำหนดเพดานเต๋าตามช่วงของสไตล์
- **Stamina:** กำหนด Stamina สูงสุดในการแข่ง และเป็นโบนัสคงที่ในผล Run
- **Power:** ลดโทษเมื่อวิ่งแซงคู่แข่งในเลนเดียวกัน
- **Gut:** ตั้งแต่ Phase 3 จะเพิ่มผล Run; เมื่อเป็น Gold จะได้เพิ่มตามจำนวนคู่แข่งใกล้ตัวสูงสุดสองคน
- **Wit:** ใช้เป็นทรัพยากร Skill และเกี่ยวข้องกับ Reroll แบบ Wit

Aptitude ของสนาม (Turf/Dirt), ระยะ และสไตล์ แปลงเป็นโบนัสให้ Power, ผลรวม Run และ Wit ตามลำดับ โดยค่าที่ใช้เป็นค่าจากโปรไฟล์ตอนเริ่มแข่ง ดูตัวคูณและสมการที่ [Formula Reference — Aptitude](#aptitude)

### Skill

ผู้เล่นมีช่อง Skill สี่ช่อง แต่ละ Skill มีค่า Wit, cooldown, เงื่อนไข, เป้าหมาย และผลของตัวเอง กดใช้ก่อน Run ในเทิร์นที่ต้องการ และระบบจะปฏิเสธหาก Wit ไม่พอ, อยู่ cooldown หรือเงื่อนไขไม่ผ่าน

ผลของ Skill อาจปรับเต๋า/ผลรวม, Stamina, ความเร็ว, Gold range, เลน หรือสถานะของเป้าหมาย ให้ดูเงื่อนไขและผลที่แน่นอนจากหน้ารายละเอียดของ Skill นั้น เพราะแต่ละรายการต่างกัน

### Zone

Zone เป็นความสามารถหนึ่งครั้งต่อการแข่งขัน และใช้ build ที่ตั้งไว้ก่อนแข่งซึ่งมีแต้มรวม 5 แต้ม แต่ละแต้มเลือกได้หนึ่งผล: โบนัสผลรวม +20, เพิ่มจำนวนเต๋าและลูกที่เลือก +1, เพิ่มทั้งพื้นและเพดานเต๋า +3, ฟื้น Stamina 1 หน่วย หรือเพิ่มความเร็วปัจจุบัน 1 ระดับ

Zone จะใส่โบนัสเต๋าไว้กับ Run ถัดไป ส่วนการฟื้น Stamina และความเร็วมีผลทันที

### Stamina

Stamina ในการแข่งขันเป็นค่าพลังงานแยกจาก Stat โดยเริ่มเต็มตาม Stat Stamina ทุกครั้งที่ Run จะจ่ายค่า Stamina พื้นฐานตามเลนเสมอ แล้วจึงบวกค่าเส้นทางและสภาพอากาศ

ถ้า Stamina ก่อน Run น้อยกว่าค่าที่ต้องจ่าย ผล Run จะถูกลดตามค่า Gut แล้ว Stamina จะถูกหักแต่ไม่ต่ำกว่า 0 การฟื้นจาก Skill และ Zone ใช้หน่วย Stamina Stat หนึ่งหน่วยต่อค่าที่ระบุ รายละเอียดตัวเลขอยู่ที่ [Formula Reference — Stamina](#stamina)

### Gold/White

ก่อน Run ระบบตรวจคู่แข่งจาก Score ณ จุดเริ่มต้นของเทิร์น หากมีคู่แข่งห่างไม่เกิน 20 Score และอยู่ห่างเลนไม่เกิน 1 จะได้ **Gold**; นอกนั้นเป็น **White**. โบนัส/ดีบัฟจาก Skill อาจเปลี่ยนระยะ Score หรือช่วงเลนนี้ได้

สีเป็นตัวเลือกตารางเต๋าตามสไตล์และ Phase ไม่ใช่โบนัสตายตัว: บางสไตล์เด่นเมื่อ Gold และบางสไตล์เด่นเมื่อ White ดูตารางทั้งหมดที่ [Formula Reference — Dice tables](#dice-tables)

### เลน, Draft และ Blocked

มีเลน 1–6; เลนเริ่มต้นมาจากลำดับออกตัวที่สุ่ม และ `/game lane` จะตั้งเลนสำหรับเทิร์นถัดไป

- **ค่า Stamina ของเลน:** เทิร์นแรกใช้ฐานเลน 2 (`100`) เสมอเพื่อให้การออกตัวเท่าเทียมกัน; ตั้งแต่เทิร์น 2 เลน 1–6 ใช้ค่า `90`, `100`, `110`, `120`, `130`, `140` ตามลำดับ แล้วจึงบวกค่าเส้นทางและสภาพอากาศ
- **Draft:** ถ้ามีคู่แข่งนำหน้าในเลนเดียวกันและอยู่ใน Gold range การใช้ Stamina ของ Run นั้นลดลง 10%
- **Blocked:** หากผล Run จะวิ่งผ่านคู่แข่งที่อยู่ข้างหน้าในเลนเดียวกัน จะถูกลดผลรวม 10% ต่อคน สูงสุด 20%; Power ลดโทษนี้ 1 จุดเปอร์เซ็นต์ต่อ Power 1 หน่วย แต่ไม่ต่ำกว่า 0%

### Rush และ Block

ใช้ได้ในช่วงสรุปเทิร์นอย่างละหนึ่งครั้งต่อการแข่งขัน

- **Rush:** ขยับ Score ไปข้างหน้าทันที โดยจ่าย 5% ของ Stamina สูงสุด (อย่างน้อย 1)
- **Block:** ใช้เมื่อมีผู้ตามหลังในเลนเดียวกันหรือเลนติดกันที่อยู่เลย Gold range แต่ห่างไม่เกิน Gold range + 20 ระบบเลือกผู้ตามหลังที่ใกล้ที่สุด แล้วให้ผู้ใช้ถอย Score เท่าที่จำเป็นเพื่อให้ระยะห่างเหลือ Gold range จึงเป็นการดึงคู่แข่งเข้ากลุ่ม ไม่ใช่การผลัก Score ของเป้าหมาย

### Reroll และ Wit Reroll

หลัง Run อาจมีปุ่ม Reroll หากไม่มีสถานะห้าม Reroll สำหรับเทิร์นนั้น ผู้เล่นเริ่มแข่งด้วย Reroll ปกติ 2 ครั้ง และ Wit Reroll 2 ครั้ง; แบบ Wit ใช้ได้เมื่อผลเต๋าพื้นฐานต่ำกว่าเกณฑ์ Wit Reroll ของตน และจะรับประกันว่าผลใหม่ดีกว่าผลเดิม ระบบจะคำนวณผลใหม่จากสถานะเดิมของเทิร์นและแทนที่ Score ของ Run เดิม

### เส้นทาง, Phase และ Score

สนามแบ่งเป็นสี่ Phase ตามสัดส่วนของจำนวนเทิร์น และแต่ละเทิร์นมีชนิดเส้นทาง เช่น ทางตรง ทางโค้ง เนินขึ้น หรือเนินลง เส้นทางกำหนดผลเฉพาะเทิร์นนั้น เช่น ค่า Stamina หรือการปรับเต๋า

Score ที่ได้จาก Run คือผลเต๋าหลังโบนัส, ผล Aptitude, Blocked และโทษ Stamina; Score สะสมคืออันดับการแข่งขัน

## Strategy Guide

- เลือกสไตล์ที่ Aptitude สูงและดูตาราง Gold/White ก่อนตัดสินใจไล่กลุ่มหรือหนีเดี่ยว; ดู [Gold/White](#goldwhite) และ [Dice tables](#dice-tables)
- ถ้า Stamina เริ่มต่ำ ให้พิจารณาเลนในก่อนยืนยันเทิร์นถัดไป หรือเกาะ Draft แทนการใช้เลนนอก; ดู [Stamina](#stamina) และ [เลน-draft-และ-blocked](#เลน-draft-และ-blocked)
- อย่าเปลี่ยนเข้าเลนเดียวกับคู่แข่งที่อยู่หน้า ถ้าผลของคุณมีแนวโน้มวิ่งผ่าน เพราะอาจเจอ Blocked
- เก็บ Zone และ Skill ไว้ใช้ใน Phase ที่สไตล์ของคุณเด่นหรือช่วงท้ายที่ต้องการผลรวมสูง
- ใช้ Rush เพื่อเร่ง Score 20 แต้ม หรือใช้ Block เพื่อยอมถอยเข้าระยะ Gold ตามจังหวะที่ต้องการ; ดูเงื่อนไขที่ [Rush และ Block](#rush-และ-block)

## Dictionary

| คำ | ความหมายสั้น ๆ | รายละเอียด |
| --- | --- | --- |
| Score | ระยะ/คะแนนสะสม ใช้จัดอันดับ | [เส้นทาง, Phase และ Score](#เส้นทาง-phase-และ-score) |
| Phase | ช่วงหนึ่งในสี่ของการแข่งขัน | [เส้นทาง, Phase และ Score](#เส้นทาง-phase-และ-score) |
| White / Gold | สีที่เลือกตารางเต๋า | [Gold/White](#goldwhite) |
| Draft | ลดค่า Stamina เมื่อวิ่งตามหลังในเลนเดียวกัน | [เลน, Draft และ Blocked](#เลน-draft-และ-blocked) |
| Blocked | โทษผลรวมเมื่อวิ่งผ่านคู่แข่งในเลนเดียวกัน | [เลน, Draft และ Blocked](#เลน-draft-และ-blocked) |
| Zone | ความสามารถใช้ได้ครั้งเดียวต่อการแข่งขัน | [Zone](#zone) |
| Wit | ทรัพยากรสำหรับ Skill และ Reroll | [Skill](#skill) |
| `d` / `kh` | จำนวนเต๋า / จำนวนลูกสูงสุดที่นำมารวม | [Dice tables](#dice-tables) |

## Formula Reference

ส่วนนี้เป็นรายการอ้างอิงเชิงตัวเลข ไม่อธิบายระบบซ้ำ; ให้อ่านความหมายและลำดับการทำงานที่ [Race Mechanics](#race-mechanics) ก่อน

### Aptitude

| Rank | G | F | E | D | C | B | A | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ตัวคูณ | 1.00 | 1.05 | 1.10 | 1.15 | 1.20 | 1.25 | 1.30 | 1.35 |

- Effective Speed = `round(Speed × Distance modifier)`
- Track acceleration = `(0.3 + 0.1 × Power) × Track modifier` per turn
- Distance bonus to Run total = `round(subtotal × Distance aptitude %)`
- Wit gain = `round((10 + 2 × Wit) × Style modifier)`
- Wit Reroll requirement = `round((25 × Wit) × Style modifier)`

### Stamina

- Maximum runtime Stamina = `(8 + Stamina stat) × 100`
- Turn 1 lane base drain: `L2 100` เสมอ; ตั้งแต่ Turn 2: `L1 90`, `L2 100`, `L3 110`, `L4 120`, `L5 130`, `L6 140`
- Path drain: Straight `0`, Curve `0`, Uphill `lane base × 2`, Downhill `lane base × 0`
- Run drain = `lane base + path cost + weather cost`; Draft drain = `round(total drain × 0.90)`
- Low-Stamina penalty = `25 − Gut` percent of the final Run total, minimum 0%
- Rush cost = `max(1, round(maximum Stamina × 0.05))`; Rush เพิ่ม Score `20`

### Dice tables

`Nd khK` หมายถึงทอย N ลูก แล้วรวม K ลูกที่สูงสุด; `Nd` หมายถึงรวมทุกลูก

| Style | White P1 | White P2 | White P3 | White P4 | Gold P1 | Gold P2 | Gold P3 | Gold P4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | 2d | 4d kh2 | 4d kh2 | 6d kh2 | 4d kh2 | 2d | 2d | 2d |
| Pace | 1d | 2d | 2d | 3d | 4d kh1 | 4d kh2 | 4d kh2 | 4d kh3 |
| Late | 1d | 2d | 4d kh2 | 4d kh3 | 1d | 2d | 6d kh2 | 6d kh3 |
| End | 1d | 1d | 4d kh3 | 6d kh3 | 1d | 1d | 2d | 6d kh4 |

สำหรับเต๋าแต่ละลูก:

- Ceiling = `floor(current max speed) + cap bonuses + path ceiling bonus − path reduction`
- Floor = `floor(Ceiling × 0.25) + path floor bonus + other floor bonuses`

| Style | P1 | P2 | P3 | P4 |
| --- | --- | --- | --- | --- |
| Front | 16 | 21 | 22 | 23 |
| Pace | 16 | 19 | 21 | 24 |
| Late | 14 | 18 | 23 | 23 |
| End | 12 | 16 | 20 | 25 |

Current max speed ใช้ค่าในตารางของสไตล์และ Phase ปัจจุบัน

ผลรวมก่อนผลเชิงเลน:

`selected dice + 2×Speed + Power + Stamina + Gut bonus + flat velocity + distance bonus + total-percent modifier`

Gut bonus ใน Phase 3–4 คือ `2×Gut` และเพิ่มอีก `2×Gut` ต่อคู่แข่ง Gold (นับสูงสุด 2 คน)

### Gold/White และเลน

- Gold range = `max(1, 20 + self bonus − enemy penalty)` Score
- Gold lane tolerance = `max(0, 1 + self bonus − enemy penalty)` เลน
- Blocked raw penalty = `min(20%, 10% × จำนวนคู่แข่งที่ถูกวิ่งผ่าน)`
- Blocked final penalty = `max(0%, raw penalty − Power%)`
- Final after Blocked = `round(pre-lane total × (1 − final penalty))`
- Block move-back = `gap to nearest eligible trailing runner − Gold range`

## Centralized Race History

Completed races are persisted once in the central Race History model. It is
the authoritative source for race detail, career history and course
leaderboards. Legacy `race_rankings` data is discarded because it lacks the
race, turn and participant detail required by this system.

- `race_history`: race/course metadata, mode, timestamps and `record_type`
  (`official` or `practice`).
- `race_participants`: race-time Uma/Mob/Trainer identity, finishing result
  and a snapshot of mutable race stats, aptitudes, skills and Zone build.
- `race_participant_turns`: completed classic-race turn scores, lane and
  position. `run_score` remains separate from cumulative score.
- `race_participant_actions`: structured Skill, Zone, lane change, Block,
  Blocked, Rush, reroll, Draft and timing events.

Official leaderboards derive one Personal Best per persistent Uma from Race
History and exclude Practice by default. Practice races are saved in full and
remain queryable, but never affect official leaderboards. Historical Uma,
Trainer and build data is always read from the snapshot saved at race time.

All newly created races default to `practice`, regardless of the selected
course. Before starting a Discord race, only the room owner can use
`/game official` to mark that lobby as an Official race. The classification is
locked once the race starts.

### Phase

`Phase = min(4, max(1, ceil(turn ÷ (max turns ÷ 4))))`
