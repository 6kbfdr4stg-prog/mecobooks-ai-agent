# 📖 HƯỚNG DẪN CÀI ĐẶT CHATBOT QUẢN LÝ TÀI CHÍNH

## Tổng quan
Chatbot Telegram quản lý tài chính cá nhân sử dụng **Gemini API** + **Google Sheets**.

### Tính năng chính:
- 📝 Nhập liệu tự nhiên: "Bán đơn sách 500k", "Ăn phở 50k"
- 🤖 AI tự phân tích và phân loại giao dịch
- 📊 Báo cáo ngày/tháng tự động
- 🔔 Nhắc nợ trước 7 ngày
- ☀️ Nhắc nhở mỗi sáng 8h
- 🏠 Theo dõi tiến độ tiền nhà
- ⚡ Cảnh báo gãy dòng tiền

---

## Bước 1: Tạo Telegram Bot

1. Mở Telegram, tìm **@BotFather**
2. Gõ `/newbot`
3. Đặt tên bot: `MecoFinanceBot` (hoặc tên bạn muốn)
4. Đặt username: `meco_finance_bot` (phải kết thúc bằng `bot`)
5. **Lưu lại Token** mà BotFather gửi cho bạn (dạng: `123456789:ABCdefGHI...`)

---

## Bước 2: Lấy Gemini API Key

1. Truy cập: https://aistudio.google.com/apikey
2. Bấm **"Get API Key"** → **"Create API Key"**
3. Chọn project hoặc tạo mới
4. **Lưu lại API Key** (dạng: `AIzaSy...`)

---

## Bước 3: Tạo Google Sheets

1. Truy cập https://sheets.google.com → Tạo spreadsheet mới
2. Đặt tên: **"Quản Lý Tài Chính - Chatbot"**
3. **KHÔNG cần tạo tab thủ công** - Code sẽ tự tạo 3 tab khi chạy lần đầu

---

## Bước 4: Copy Code vào Apps Script

1. Trong Google Sheets, vào menu **Tiện ích mở rộng** → **Apps Script**
2. Xóa hết code mặc định trong file `Code.gs` (hoặc `Mã.gs`)
3. Copy toàn bộ nội dung từ file **`AllInOne.gs`** dán vào đó.
4. Bấm 💾 **Lưu** (biểu tượng đĩa mềm)

*(Bạn không cần tạo nhiều file nữa, tất cả đã được gộp làm một)*

---

## Bước 5: Cấu hình API Keys

Mở file `Config.gs` và thay thế 3 dòng sau:

```javascript
const GEMINI_API_KEY = "DÁN_GEMINI_API_KEY_VÀO_ĐÂY";    // ← Dán API key Gemini
const TELEGRAM_TOKEN = "DÁN_TELEGRAM_BOT_TOKEN_VÀO_ĐÂY"; // ← Dán Token từ BotFather
## Bước 5: Cấu hình Chat ID

Mở file `Config.gs`, bạn sẽ thấy API Key và Token đã được điền sẵn.

Bạn chỉ cần điền **OWNER_CHAT_ID** (lấy ở Bước 7):

```javascript
const OWNER_CHAT_ID = "DÁN_CHAT_ID_VÀO_ĐÂY"; // ← Lấy ở Bước 7
```

1. Trong Apps Script, chọn hàm **`initializeSheets`** từ dropdown phía trên
2. Bấm **▶ Run** (nút chạy)
3. Cấp quyền khi được hỏi (bấm "Review Permissions" → Chọn tài khoản → "Allow")
4. Kiểm tra Google Sheets: phải có 3 tab mới: **Transaction**, **Dashboard**, **Debt**

---

## Bước 7: Lấy Chat ID

1. Mở Telegram, tìm bot bạn vừa tạo
2. Gửi tin nhắn `/start` cho bot
3. Quay lại Apps Script, chọn hàm **`getUpdates`** → Bấm **▶ Run**
4. Xem kết quả trong **Execution Log**: sẽ hiện `✅ CHAT ID CỦA BẠN: 123456789`
5. Copy số đó, dán vào `OWNER_CHAT_ID` trong `Config.gs`

---

## Bước 8: Deploy Webapp

1. Trong Apps Script, bấm **Deploy** → **New deployment**
2. Bấm biểu tượng ⚙️ → chọn **Web app**
3. Cấu hình:
   - **Description**: Financial Chatbot
   - **Execute as**: Me
   - **Who has access**: **Anyone** ← QUAN TRỌNG!
4. Bấm **Deploy**
5. **Copy URL webapp** (dạng: `https://script.google.com/macros/s/AKfyc.../exec`)

---

## Bước 9: Kết nối Webhook

### Cách 1: Qua trình duyệt
Dán URL sau vào trình duyệt (thay TOKEN và URL):
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL_WEBAPP>
```

### Cách 2: Qua Apps Script
1. Mở file `Code.gs`
2. Tìm hàm `setWebhookManual()`, thay `DÁN_URL_WEBAPP_VÀO_ĐÂY` bằng URL webapp
3. Chọn hàm **`setWebhookManual`** → Bấm **▶ Run**
4. Kiểm tra: phải thấy `"ok": true` trong Log

---

## Bước 10: Thiết lập Nhắc nhở Tự động

1. Trong Apps Script, bấm ⏰ **Triggers** (thanh bên trái)
2. Bấm **+ Add Trigger** và tạo 3 trigger:

### Trigger 1: Nhắc nhở sáng
| Cấu hình | Giá trị |
|-----------|---------|
| Function | `sendDailyReminder` |
| Event source | Time-driven |
| Type | Day timer |
| Time of day | 8am to 9am |

### Trigger 2: Cảnh báo nợ
| Cấu hình | Giá trị |
|-----------|---------|
| Function | `sendDebtAlert` |
| Event source | Time-driven |
| Type | Day timer |
| Time of day | 7am to 8am |

### Trigger 3: Báo cáo tối
| Cấu hình | Giá trị |
|-----------|---------|
| Function | `sendEveningReport` |
| Event source | Time-driven |
| Type | Day timer |
| Time of day | 9pm to 10pm |

---

## Bước 11: Test Bot

1. Mở Telegram, vào chat với bot
2. Thử các lệnh:

```
/help          → Xem danh sách lệnh
/bc            → Báo cáo hôm nay
/no            → Bảng tổng hợp nợ
/nha           → Tiến độ tiền nhà
/mt            → Mục tiêu & KPI
/risk          → Kiểm tra rủi ro
/tuvan         → Xin lời khuyên AI
```

3. Thử nhập giao dịch:
```
Bán đơn sách 500k
Ăn phở 50k
Cafe 35k
Nhận share VP 2tr
```

---

## Khắc phục lỗi thường gặp

### Bot không phản hồi
- Kiểm tra webhook: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Đảm bảo "Who has access" = **Anyone**
- Kiểm tra Execution Log trong Apps Script

### Lỗi "Authorization required"
- Chạy lại bất kỳ hàm nào → Bấm "Review Permissions" → Allow

### Gemini trả về lỗi
- Kiểm tra API Key đúng chưa
- Kiểm tra quota tại https://aistudio.google.com

### Lỗi "Sheet not found"
- Chạy hàm `initializeSheets()` lại

---

## Cập nhật khi trả xong nợ

Khi bạn trả xong một khoản nợ, mở `Config.gs` và cập nhật:
- Đặt `balance: 0` cho khoản đã trả
- Đặt `monthlyPayment: 0`
- Tính lại `BUSINESS.targetDailyAccumulation`

Ví dụ khi trả xong TCB:
```javascript
{
  name: "TCB",
  balance: 0,           // ← Đã trả xong
  monthlyPayment: 0,    // ← Không cần trả nữa
  ...
}
```
