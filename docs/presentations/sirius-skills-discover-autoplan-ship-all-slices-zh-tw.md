# 10 分鐘簡報：在 `sirius-skills` 中用 `bootstrap`、`discover`、`autoplan` 與 **「Ship all slices」** 推動功能 / 子功能交付

## 0. 開場（約 1 分鐘）

大家好，今天我想介紹的是 **[`sirius-skills`](https://github.com/sirius-cc-wu/sirius-skills)** 這個 GitHub 儲存庫。

`sirius-skills` 是一套用來支援 **規格驅動開發** 的 skills 集合。它把工作拆成清楚的**規劃階段**與**執行階段**，讓程式代理（coding agent）不只是會寫程式，而是能沿著明確流程，把工作穩定地推進到完成。

如果只用一句話總結今天的主題，就是：

> **先用 `bootstrap` 初始化 repo 並建立 wiki，再用 `discover` 把功能（`feature`）或子功能（`subfeature`）的問題與範圍定義清楚，再用 `autoplan` 把規劃一路推進到可執行狀態，最後對程式代理說一句「Ship all slices」，讓它在自動駕駛模式下持續把所有切片做完。**

今天我會聚焦四件事：

1. `bootstrap`
2. `discover`
3. `autoplan`
4. **「Ship all slices」** 的實際意思

---

## 1. 為什麼是 `sirius-skills`（約 1 分鐘）

`sirius-skills` 的價值，就是把整件事拆成清楚的階段：

- `bootstrap`：初始化 repo 設定，並建立 wiki 骨架
- `discover`：定義問題與範圍
- `design` / `breakdown`：整理設計與切片
- `autoplan`：自動推進規劃負責技能鏈
- `ship`：把已核准的待辦切片一片一片做完

但我認為，`sirius-skills` 和很多其他 SDD 方法最大的不同之一是：

> **它假設開發人員需要做程式查核，所以不只重視文件存在，更重視文件能不能幫助人快速理解。**

因此在 `sirius-skills` 裡，`system-design.md` 與 `blueprint.md` 會特別強調 UML 圖。目的不是把文件寫得更漂亮，而是降低開發人員在審查設計與程式碼時的理解負擔。

所以它不是單一 skill，而是一條從想法到交付、也支援人工程式查核的工作流水線。

---

## 2. 一開始先用 `bootstrap`（約 1 分鐘）

在我看來，`sirius-skills` 的正確起點不是直接進 `discover`，而是先做：

> **`bootstrap`，而且要請它一起建立 wiki。**

`bootstrap` 會幫 repo 建立：

- `.skills/planning.json`
- `.skills/execution.json`
- `.skills/conventions.json`

如果同時要求建立 wiki，還會一起建立 wiki 骨架，讓後續知識整理有固定位置。

> **先 `bootstrap`，而且一開始就把 wiki 建好，後面的 planning、review 與知識整理都會順很多。**

---

## 3. 功能（`feature`）與子功能（`subfeature`）是什麼（約 1 分鐘）

在 `sirius-skills` 裡，有兩個很重要的層級：

### 功能（`feature`）

`feature` 是主要功能規劃單位，通常放在：

```text
docs/features/<feature-slug>/
```

它會承載主要規劃文件，例如：

- `discover.md`
- `user-stories.md`
- `system-design.md`
- `slice-planning.md`
- `slice-traceability.md`

### 子功能（`subfeature`）

`subfeature` 是掛在既有 `feature` 底下的持久子範圍，用來處理：

- 後續增量需求
- 範圍收斂或替換
- 已完成功能的後續工作
- 補強既有行為或修補流程

通常位置會在：

```text
docs/features/<feature-slug>/subfeatures/<subfeature-id>/
```

所以可以把它簡單理解成：

> `feature` 是主功能包，`subfeature` 是同一功能脈絡下的後續子工作包。

---

## 4. 表達方式（Representation）（約 1 分鐘）

在 `sirius-skills` 裡，我們不只是在「做事情」，也很重視「怎麼把事情表達清楚」。

同一個 `feature` 或 `subfeature`，會用不同文件承載不同層次的資訊：

- `discover.md`：描述問題、目標、限制與故事
- `system-design.md`：描述系統設計、架構、介面與風險
- `blueprint.md`：描述單一執行切片的細部設計、實作步驟與驗證方式

其中 `design` 與 `blueprint` 都很重 UML，因為 UML 圖對人類理解設計通常比純文字更快。

這也是 `sirius-skills` 很有特色的一點：它不是假設代理做完就結束，而是預設**人還要進來做程式查核**。因此系統設計與細部設計的 UML 圖，不只是設計產物，也是快速理解程式與結構的重要輔助材料。

你可以把它理解成：

> `discover` 主要回答「要解決什麼問題」，`design` 主要回答「系統怎麼設計」，`blueprint` 主要回答「這一片要怎麼做」。

---

## 5. `discover` 是做什麼的（約 2 分鐘）

`discover` 的角色是：

> **在設計與實作之前，先把功能或子功能的問題、目標、限制與故事講清楚。**

它最常產出的文件是：

- `<feature_path>/discover.md`
- `<feature_path>/user-stories.md`

其中 `<feature_path>` 可以是：

- 一個 `feature`
- 或一個 `subfeature`

### `discover` 主要處理什麼

它會整理：

- 問題與目標
- 範圍與非目標
- 使用者、利害關係人與限制
- 初步故事與能力邊界

也就是說，`discover` 的工作不是寫技術細節，而是把模糊需求變成清楚的**規劃輸入**。

### 對 `feature` 與 `subfeature` 的差別

- 對 **`feature`** 來說，`discover` 是完整定義新功能的起點。
- 對 **`subfeature`** 來說，`discover` 更像是在既有功能脈絡下，補充這次變更的目的、影響範圍、取代了什麼、收斂了什麼、或新增了什麼。

### 一句話總結

> `discover` 是定義問題的地方，不是直接開始解決問題的地方。

---

## 6. `autoplan` 是做什麼的（約 2 分鐘）

如果說 `discover` 是把問題講清楚，
那 `autoplan` 就是：

> **把單一 `feature` 或 `subfeature` 的規劃資料包自動往前推，直到遇到真正需要人工停下來的邊界。**

它的責任可以簡化成三件事：

- 判斷目前規劃狀態
- 找出下一個規劃負責技能
- 一路往前推到真正需要人工停下來的邊界

### 常見的負責技能鏈

對 **正式 `feature`**，常見流程是：

```text
discover -> design -> breakdown -> review-planning
```

對 **`subfeature`**，常見流程是：

```text
discover -> assess -> design -> breakdown -> review-planning
```

這裡有一個重點：

- `feature` 通常直接往 `design` 前進
- `subfeature` 常常先進 `assess`，先分析它對既有 `feature` 的影響，再繼續設計與切片

### `autoplan` 的真正價值

它不是只回報「下一步是什麼」，而是：

> **在自動駕駛條件下，把規劃階段的負責技能串起來，一路往前跑。**

直到碰到這些真正停點：

- 需要人工核准
- 需要提交規劃文件
- 有不能自動修復的驗證失敗
- 有真的需要人判斷的模糊點

所以 `autoplan` 是**規劃加速器**，不是規劃的**唯一真實來源**。

---

## 7. 什麼是 **「Ship all slices」**（約 2 分鐘）

這是我平常最常對程式代理說的一句話：

> **Ship all slices**

在 `sirius-skills` 的語境裡，這句話背後的意思不是：

- 一次把整包功能全部亂做完
- 跳過審查、提交與職責邊界

它真正代表的是：

> **讓代理在自動駕駛模式下，反覆執行 `ship`，持續推進同一個已核准、已提交的 `feature` 或 `subfeature` 待辦清單，直到所有已規劃切片完成，或者遇到明確的人工邊界。**

### `ship` 真正做的事

`ship` 是**待辦清單協調器**。它會：

- 讀取這個 `feature` 或 `subfeature` 的已規劃切片
- 先看增量順序
- 再看切片依賴順序
- 決定下一片是誰
- 如果需要就 bootstrap 下一個切片
- 把目前切片交給下一位具體 owner

例如：

- `brief`
- `blueprint`
- 實際程式碼實作
- `review-execution`
- `close-slice`
- `commit`

### 所以「Ship all slices」的實際含義是

> 不是一次做完全部，而是**一次做一片，但持續做完整個待辦清單**。

它同時保留了**自動化推進**與**清楚的執行邊界**。

---

## 8. `ship` 適用於 `feature` 與 `subfeature`（約 1 分鐘）

這一點很適合在簡報中特別強調。

在 `sirius-skills` 裡，`ship` 可以處理的是：

> **一個已經完成審查、也已經提交的 `feature` 或 `subfeature` 待辦清單。**

所以你可以：

- 對一個完整 `feature` 說：**Ship all slices**
- 也可以對某個已規劃完成的 `subfeature` 說：**Ship all slices**

這很重要，因為實際工作中很多情境不是全新功能，而是：

- 已完成功能的後續延伸
- 補一個缺漏
- 收斂一段流程
- 修正某個設計

這些都非常適合走 `subfeature`。

### 一句話整理

> `feature` 用來承載主要功能規劃，`subfeature` 用來承載後續增量工作；兩者在規劃完成後，都可以交給 `ship` 逐切片推進。

---

## 9. 我實際上的使用方式（約 1 分鐘）

如果講我自己平常怎麼用 `sirius-skills`，重點其實是：**先確認 LLM 真的理解需求，再放心讓它自動推進。**

1. 先用 `bootstrap` 初始化 repo，並要求它把 wiki 一起建立起來。
2. 先看 `user-stories.md`，確認需求、範圍與故事沒有偏掉。
3. 再執行 `autoplan`，把規劃往前推。
4. 規劃完成後，重點檢查 `system-design.md` 的 UML 圖與 `slice-planning.md` 的切片。
5. 確認沒偏離之後，再核准、提交，然後說一句 **Ship all slices**。
6. 做程式審查時，我會看每個 slice 的 `brief.md` 裡的工作項目，以及 `blueprint.md` 裡的 UML 圖，快速理解這片原本要做什麼，以及程式碼是否照著設計走。

---

## 10. 可以展示的底層命令（約 30 秒）

如果你想在示範裡補充底層命令，可以展示：

```bash
python3 skills/bootstrap/scripts/bootstrap.py --mode default --wiki
```

接著進入規劃加速：

```bash
python3 skills/autoplan/scripts/autoplan.py <target> --execute-owner-chain --json
```

規劃核准並提交後，進入執行：

```bash
python3 skills/ship/scripts/ship.py <target> --resume --json
```

如果是對代理下高階指令，我通常直接說：

```text
Ship all slices
```

而 `<target>` 可以是：

- 一個 `feature`
- 或一個 `subfeature`

---

## 11. 結尾（約 30 秒）

最後，我想用一句話收尾：

> **`sirius-skills` 的價值，不只是讓 AI 會寫程式，而是讓 AI 能沿著清楚的 `feature` / `subfeature` 規劃邊界，把工作穩定地推進到完成。**

所以最推薦的心智模型是：

- 先用 `bootstrap` 初始化 repo，並把 wiki 一起建立起來
- 先用 `user-stories.md` 確認需求真的被理解
- 再用 `autoplan` 把規劃一路推進到可執行狀態
- 審核 `system-design.md` 的 UML 與 `slice-planning.md` 的切片
- 最後用 **Ship all slices** 讓代理逐切片、安全地完成整個待辦清單

而 `sirius-skills` 最值得記住的特色之一，就是它把 UML 圖當成降低人工審查成本的重要工具，而不是可有可無的裝飾。

---

# 簡短版講者備忘稿

> 今天我要介紹的是 `sirius-skills`，GitHub 位址是：https://github.com/sirius-cc-wu/sirius-skills 。它是一套支援規格驅動開發的 skills 集合。我認為它和很多其他 SDD 方法最大的不同，是它預設開發人員需要做程式查核，所以會特別強調 `system-design.md` 與 `blueprint.md` 裡的 UML 圖，用來降低人工理解負擔。實際使用上，我會先用 `bootstrap` 初始化 repo，並要求它把 wiki 一起建立起來；接著看 `user-stories.md`，確認 LLM 是否真的理解需求；再用 `autoplan` 把規劃往前推。規劃完成後，我會重點看 `system-design.md` 的 UML 圖與 `slice-planning.md` 的切片，確認設計和執行沒有偏離；之後才核准、提交，並對程式代理說一句 **Ship all slices**。做程式審查時，我會看每個 slice 的 `brief.md` 工作項目，以及 `blueprint.md` 的 UML 圖，快速理解這片程式到底在做什麼。

---

# 附錄：PlantUML server 參考資料

因為 `design` 與 `blueprint` 都很重 UML，所以本機有一個可用的 PlantUML server 很重要。

這個 repo 的本機工具假設是：

```text
http://127.0.0.1:8080
```

也就是說，如果你的本機已經有 PlantUML server 跑在 `127.0.0.1:8080`，就可以直接拿來做圖形驗證。

如果本機還沒有啟動，可以用 Docker 很快跑起來：

```bash
docker run --rm -d \
  --name plantuml-server \
  -p 8080:8080 \
  plantuml/plantuml-server:jetty
```

啟動後可以用瀏覽器打開：

```text
http://127.0.0.1:8080
```

如果要停止：

```bash
docker stop plantuml-server
```

補充提醒：

- `design` 主要在 `system-design.md` 裡放 PlantUML 圖
- `blueprint` 主要在 `blueprint.md` 裡放 PlantUML 圖
- 寫完 UML 後，最好用本機 PlantUML server 檢查圖是否能正確渲染

---

# 附錄：`simplify` skill 參考資料

`simplify` 是用來對目前 branch 或 PR 的變更做**最後一輪精簡**的 skill。

很適合用在這幾個時機：

- 開 PR 之前
- 根據 review feedback 做整理時
- 像這次一樣，對簡報或文件做最後簡化時

它的重點不是改變行為，而是：

- 刪掉重複
- 收斂表達
- 保留原本意圖
- 讓變更更容易審查

`simplify` 的做法可以理解成三步：

1. 先看目前 diff，鎖定變更範圍與不可以破壞的行為。
2. 從重用、品質、效率、架構貼合度四個角度找出真正值得簡化的地方。
3. 只做高價值修正，並確認外部行為沒有改變。

如果用一句話來記：

> **`simplify` 不是重寫，而是把已經改好的東西整理得更清楚、更短、更容易審查。**
