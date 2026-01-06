1. Tên đề tài 
Hệ thống giám sát an ninh bằng cảm biến chuyển động PIR (mô phỏng) 
2. Nội dung lý thuyết - Kiến trúc IoT nhiều lớp: cảm biến (PIR) → mạng (MQTT) → cloud → 
dashboard. - Nguyên lý cảm biến PIR: phát hiện chuyển động dựa trên bức xạ hồng 
ngoại từ cơ thể người. - Cơ chế giám sát an ninh: khi phát hiện chuyển động → gửi tín hiệu cảnh 
báo. - Giao thức MQTT: truyền sự kiện 0/1 (không có chuyển động / có chuyển 
động). - Lưu trữ dữ liệu sự kiện: cloud hoặc file log. - Ứng dụng AI: phân loại hành vi bình thường (người trong nhà) và bất 
thường (xâm nhập ngoài giờ). 
3. Nội dung thực hành - Bước 1: Mô phỏng dữ liệu PIR bằng Node-RED hoặc Python (0 = không 
có chuyển động, 1 = có chuyển động). - Bước 2: Publish dữ liệu lên MQTT Broker với topic ví dụ 
'iot/nhomXX/security/pir'. - Bước 3: Subscriber nhận dữ liệu và hiển thị trên dashboard (trạng thái 
phòng: An toàn / Cảnh báo). - Bước 4: Thiết lập cảnh báo (icon đỏ, còi ảo, hoặc notification) khi có 
chuyển động bất thường. - Bước 5: Log dữ liệu sự kiện (CSV hoặc database). - Bước 6: (Tùy chọn) áp dụng mô hình AI classification để phân biệt chuyển 
động hợp lệ/bất thường. 
4. Dataset - Dữ liệu mô phỏng: binary (0/1) kèm timestamp. - Ví dụ JSON: 
{ "timestamp": "2025-09-10T09:30:00Z", "motion": 1 } - Dataset tham khảo: UCI Human Activity Recognition (HAR). - Ứng dụng AI: Logistic Regression, Decision Tree để phân loại hoạt động. 
5. Yêu cầu nhóm và học viên - Nghiên cứu nguyên lý PIR và ứng dụng trong IoT an ninh. - Hoàn thành mô hình mô phỏng PIR → Broker → Dashboard. - Dashboard phải hiển thị trạng thái phòng và cảnh báo. - Có log dữ liệu sự kiện an ninh. - Nộp báo cáo mô tả kiến trúc, biểu đồ trạng thái, demo tình huống xâm 
nhập. - (Tùy chọn) AI classification để phân biệt hành vi hợp lệ/bất thường.