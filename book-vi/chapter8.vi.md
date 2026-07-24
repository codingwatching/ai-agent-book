# Sự tiến hóa liên tục của Agent

Agent ngày nay đối mặt với một nghịch lý năng lực rõ rệt: nó có thể giải quyết zero-shot những nhiệm vụ phức tạp chưa từng gặp, nhưng sau khi xử lý mười nghìn nhiệm vụ tương tự, ngày hôm sau vẫn có thể lặp lại sai lầm của ngày đầu tiên. **Khả năng tự chủ học hỏi từ kinh nghiệm** đang trở thành năng lực then chốt để Agent chuyển từ “biết hoàn thành nhiệm vụ” sang “có thể làm việc đáng tin cậy”, đồng thời là chủ đề nghiên cứu cốt lõi của thế hệ mô hình tiếp theo. Tuy nhiên, năng lực học liên tục của bản thân mô hình hiện vẫn còn rất hạn chế.

Nguyên nhân trước hết là mô hình sau khi triển khai không tự động thay đổi tham số chỉ vì một lần suy luận. Học trong ngữ cảnh, duy trì trạng thái và nén được thảo luận ở Chương 2 có thể giúp Agent thích nghi **trong nhiệm vụ hiện tại**; nhưng khi ngữ cảnh kết thúc, thay đổi này không tự nhiên được chuyển sang nhiệm vụ tiếp theo. Lưu hội thoại vào bộ nhớ cũng không đồng nghĩa với việc đã học được hành vi mới: quỹ đạo gốc có thể rất dài, chứa cả chiến lược hiệu quả, thành công ngẫu nhiên, quy kết sai và đầu vào không đáng tin cậy.

Vậy tại sao không để mô hình tự huấn luyện sau mỗi nhiệm vụ? Bởi môi trường sản xuất hiếm khi cung cấp tín hiệu học tập sạch. Người dùng hài lòng không có nghĩa là tuân thủ quy định; kiểm thử vượt qua cũng có thể do các ca kiểm thử thất bại đã bị xóa. Một lần cập nhật cục bộ còn có thể gây quên năng lực, trôi dạt chiến lược hoặc suy giảm an toàn. Nếu cho phép mô hình đang vận hành trực tiếp sửa đổi chính nó dựa trên phản hồi chưa được xác minh, kinh nghiệm sai và tấn công chèn Prompt có thể bị củng cố, rồi tiếp tục khuếch đại trong các nhiệm vụ sau. Việc huấn luyện định kỳ mô hình nền tảng có thể nâng cao năng lực tổng quát, nhưng không thể kịp thời hấp thụ các quy tắc riêng, thay đổi công cụ và kinh nghiệm cục bộ mà mỗi Agent gặp hằng ngày.

Vì vậy, khi bản thân mô hình chưa thể học liên tục một cách đáng tin cậy, trước hết cần kiến tạo “học tập” thành một hệ thống có kiểm soát bao quanh mô hình: ghi lại bằng chứng vận hành, xác minh kết quả và quá trình, rút ra điểm chung từ nhiều quỹ đạo, rồi quyết định nên cập nhật tri thức, chỉ dẫn, chương trình hay tham số mô hình. Mọi sửa đổi trước tiên đều phải hình thành phiên bản ứng viên; chỉ sau khi vượt qua kiểm thử hồi quy và kiểm tra an toàn mới được phép thay đổi lần vận hành tiếp theo. Đây không phải sự thay thế cho năng lực học của mô hình, mà là con đường kỹ thuật giúp Agent có được năng lực học liên tục trong điều kiện công nghệ hiện tại.

Các chương trước đã trình bày những thành phần chủ yếu cần thiết cho hệ thống này. Chương 2 xử lý trạng thái trong nhiệm vụ, Chương 3 cung cấp hạ tầng tri thức, Chương 5 trao cho Agent siêu năng lực tạo công cụ và sửa đổi hệ thống, Chương 6 thiết lập đánh giá và xác minh, còn Chương 7 trình bày cách cập nhật tham số mô hình. Nhiệm vụ của Chương 8 là tổ chức các thành phần này thành vòng khép kín tiến hóa liên tục như minh họa trong Hình 8-1.

![Hình 8-1 Vòng khép kín tổng thể của quá trình tiến hóa liên tục của Agent](images/fig8-1.svg)

Tiến hóa liên tục cần xuất phát từ kinh nghiệm vận hành có thể truy vết, có khả năng thay đổi hành vi về sau và đã được xác minh là không gây suy giảm rõ rệt. Chương này trước hết thảo luận cách xác định một lần vận hành tốt ở đâu, sai ở đâu; sau đó so sánh bốn phương pháp cập nhật cùng phạm vi áp dụng; cuối cùng bàn về cách các cập nhật này được xác minh, phát hành, sửa đổi và loại bỏ trong quá trình vận hành dài hạn.

## Thu nhận tín hiệu học tập từ quỹ đạo vận hành

Điểm khởi đầu của tiến hóa liên tục không phải là “tổng kết”, mà là “đánh giá”. Nếu hệ thống không biết nhiệm vụ đã hoàn thành hay chưa, cũng không biết bước nào tạo nên thành công hoặc thất bại, thì phần phản tư do mô hình ngôn ngữ tạo ra chỉ có thể là một phỏng đoán. Một khi đánh giá sai đi vào tri thức dài hạn, Prompt hệ thống hoặc dữ liệu huấn luyện, ảnh hưởng của nó sẽ liên tục khuếch đại qua các nhiệm vụ sau.

Kết quả của một số nhiệm vụ tương đối dễ xác minh. Coding Agent có thể chạy kiểm thử, kiểm tra kiểu và benchmark hiệu năng; Agent thay người dùng xử lý hoàn tiền có thể truy vấn trạng thái đơn hàng và số tiền hoàn thực tế. Những tín hiệu này đến từ trạng thái thực trong môi trường và thường đáng tin cậy hơn lời mô tả của mô hình về hành vi của chính nó. Tuy nhiên, kết quả đúng không có nghĩa là quá trình đúng. Xóa các ca kiểm thử thất bại cũng có thể khiến kiểm thử vượt qua; lời hứa miệng với người dùng rằng “chúng tôi sẽ hoàn tiền trong vòng 7 ngày, xin vui lòng chờ đợi” cũng có thể tạm thời nhận được phản hồi hài lòng. Vì vậy, đánh giá đáng tin cậy phải xem xét cả kết quả lẫn con đường đạt được kết quả đó.

Nhiều nhiệm vụ hơn không có một đáp án đúng duy nhất. Nhân viên chăm sóc khách hàng có kiên nhẫn hay không, có cung cấp phương án linh hoạt trong phạm vi tuân thủ hay không, báo cáo nghiên cứu có nắm bắt bằng chứng then chốt hay không, văn bản được tạo có tự nhiên và súc tích hay không, tất cả đều cần được phán đoán theo ngữ cảnh. Khi đó có thể sử dụng LLM-as-a-Judge được giới thiệu ở Chương 6, nhưng không nên chỉ yêu cầu giám khảo đưa ra một tổng điểm mơ hồ. Cách hiệu quả hơn là định nghĩa trước thang đánh giá (Rubric), yêu cầu bộ xác minh chấm điểm theo từng mục, trích dẫn bằng chứng từ quỹ đạo và nêu rõ sự không chắc chắn khi thiếu bằng chứng.

Hình 8-2 trình bày một cấu trúc xác minh ba tầng. Bộ xác minh kết quả ở tầng dưới đọc kết quả kiểm thử, trạng thái cơ sở dữ liệu và phản hồi của công cụ để trả lời “việc đó có thực sự được hoàn thành hay không”; bộ xác minh quá trình ở tầng giữa kiểm tra quy tắc nghiệp vụ, quyền hạn và chuỗi hành động để trả lời “việc đó có được hoàn thành theo cách được phép hay không”; bộ xác minh chất lượng ở tầng trên đánh giá ngôn ngữ và chiến lược theo Rubric để trả lời “việc đó có được xử lý phù hợp hay không”. Chỉ số càng gần tầng dưới càng nên dựa vào mã và chân trị của môi trường; chỉ những phần khó hình thức hóa mới nên giao cho mô hình ngôn ngữ.

![Hình 8-2 Xác minh quỹ đạo ba tầng từ kết quả môi trường đến LLM Rubric](images/fig8-2.svg)

Lấy Agent chăm sóc khách hàng làm ví dụ, một Rubric hữu ích tối thiểu phải bao quát các chiều trong Bảng 8-1. Năm mục đầu chủ yếu ràng buộc giới hạn tối thiểu, hai mục cuối đo lường chất lượng dịch vụ. Cách phân tách này có giá trị chẩn đoán cao hơn câu hỏi “người dùng có hài lòng hay không”: người dùng có thể hài lòng vì Agent hoàn tiền trái quy định, cũng có thể không hài lòng vì các hạn chế tuân thủ; một chỉ số hài lòng duy nhất không thể phân biệt hai trường hợp.

Bảng 8-1 Các chiều đánh giá quỹ đạo của Agent chăm sóc khách hàng

| Chiều | Câu hỏi xác minh | Bằng chứng chính |
|---|---|---|
| Kết quả nhiệm vụ | Yêu cầu cốt lõi của người dùng đã được giải quyết hay chưa | Trạng thái môi trường cuối cùng, kết quả công cụ |
| Tuân thủ quy tắc | Có vi phạm chính sách, quyền hạn hoặc quy trình bắt buộc hay không | Kho chính sách, quỹ đạo hành động |
| Ranh giới quyền riêng tư | Có tiết lộ thông tin không được phép cung cấp hay không | Văn bản phản hồi, nhật ký truy cập dữ liệu |
| Độ tin cậy thực tế | Phát biểu có được tri thức hoặc kết quả công cụ hỗ trợ hay không | Nguồn trích dẫn, phản hồi của công cụ |
| Tính nhất quán giữa cam kết và hành động | Thao tác được tuyên bố là đã hoàn thành có thực sự diễn ra hay không | Đối chiếu phản hồi với nhật ký công cụ |
| Chất lượng diễn đạt | Có tự nhiên, súc tích, tránh lặp lại và khuôn mẫu hay không | Toàn bộ hội thoại, Rubric ngôn ngữ |
| Linh hoạt trong tuân thủ | Khi phương án ban đầu không khả thi, có tìm được lộ trình thay thế được phép hay không | Mục tiêu người dùng, chính sách và hành động tiếp theo |

Trong đó, “tính nhất quán giữa cam kết và hành động” đặc biệt phù hợp với bối cảnh Agent. Đánh giá văn bản truyền thống chỉ đọc phản hồi cuối cùng nên dễ coi “tôi đã gửi yêu cầu hoàn tiền cho bạn” là dịch vụ tốt; đánh giá quỹ đạo sẽ tiếp tục kiểm tra công cụ hoàn tiền có thực sự được gọi hay không, lệnh gọi có thành công hay không và trạng thái đơn hàng có thay đổi hay không. “Linh hoạt trong tuân thủ” cũng không nhằm khuyến khích mô hình tùy tiện vượt qua quy tắc, mà yêu cầu nó hiểu mục tiêu thực sự của người dùng và kiểm tra các lựa chọn hợp lệ như đổi lịch, gia hạn hoặc bồi thường một phần khi không thể hoàn tiền.

Kết quả xác minh không nên bị nén thành một đại lượng vô hướng. Một lần đánh giá quỹ đạo giống một bản chẩn đoán có cấu trúc hơn: nhiệm vụ thành công một phần, tuân thủ quy tắc đạt yêu cầu, nhưng có một phát biểu không có bằng chứng, một cam kết sai sự thật và phần phản hồi còn lặp lại lời giải thích chính sách ba lần. Tín hiệu đa chiều vừa giữ lại bản chất vấn đề, vừa giữ lại vị trí bằng chứng. Chỉ khi đó mô-đun phía sau mới có thể tiếp tục phán đoán: phát biểu không có bằng chứng là do thiếu tri thức, thiếu yêu cầu trích dẫn hay năng lực mô hình chưa đủ; cam kết sai sự thật nên được sửa trong Prompt hay cần bổ sung kiểm tra tính nhất quán giữa phản hồi và trạng thái công cụ trong Harness.

Bản thân bộ xác minh LLM cũng cần được hiệu chuẩn. Hệ thống sản xuất thường chuẩn bị một tập nhỏ quỹ đạo do chuyên gia gán nhãn để kiểm tra tính nhất quán của bộ xác minh trên từng chiều; các trường hợp rủi ro cao hoặc độ tin cậy thấp được chuyển cho mô hình thứ hai hoặc con người rà soát; sau khi thay đổi phiên bản mô hình, tập hiệu chuẩn được chạy lại. Bộ xác minh chịu trách nhiệm đưa ra đánh giá và bằng chứng; còn việc cần sửa đổi phần nào của Agent phải do mô-đun chẩn đoán và tiến hóa độc lập quyết định, tránh để cùng một mô hình vừa làm trọng tài vừa trực tiếp viết lại quy tắc.

> **Thí nghiệm 8-1 ★★: Xây dựng bộ xác minh quỹ đạo cho Agent chăm sóc khách hàng**
>
> Thí nghiệm này sử dụng các quỹ đạo chăm sóc khách hàng có bản ghi gọi công cụ để xây dựng bộ xác minh ba tầng “kết quả môi trường — quy tắc quá trình — chất lượng ngôn ngữ”. Phần xác định đọc trạng thái cuối cùng của đơn hàng và nhật ký công cụ để kiểm tra việc hoàn tiền, đổi lịch có thực sự diễn ra hay không; phần quy tắc đối chiếu chính sách nghiệp vụ để kiểm tra quyền hạn và các bước bắt buộc; bộ xác minh LLM đánh giá từng mục theo Bảng 8-1 và trích dẫn lượt hội thoại cụ thể cho mỗi điểm bị trừ. Thí nghiệm cần chuẩn bị một tập quỹ đạo do chuyên gia gán nhãn để hiệu chuẩn, đồng thời so sánh mức độ hỗ trợ chẩn đoán nguyên nhân gốc của hai kiểu đầu ra: “chỉ đưa tổng điểm” và “đánh giá đa chiều kèm bằng chứng”. Trọng tâm nghiệm thu không phải là cách diễn đạt của Judge hoàn toàn nhất trí với chuyên gia, mà là các vi phạm trọng yếu, cam kết sai sự thật và từ chối quá mức có thể được nhận diện ổn định.
>
> Phần triển khai đi kèm nằm tại [`trajectory-verifier`](../chapter8/trajectory-verifier/), mặc định sử dụng Judge chất lượng có thể tái lập ngoại tuyến; dùng `--judge llm` để chạy bộ xác minh LLM thực đã được triển khai.

## Bốn phương pháp tiến hóa liên tục của Agent

Tín hiệu học tập cho biết Agent cần thay đổi, nhưng không cho biết thay đổi nên diễn ra ở đâu. Căn cứ hàng đầu để lựa chọn cách cập nhật không phải là kinh nghiệm đã xuất hiện bao lâu, mà là năng lực mục tiêu có thể được biểu đạt tự nhiên bằng vật mang nào. Sự kiện và kinh nghiệm phù hợp để viết thành tài liệu tri thức; chiến lược có thể diễn đạt rõ ràng bằng ngôn ngữ phù hợp để đưa vào Prompt hoặc Skill; quy trình và ràng buộc có thể thực thi chính xác phù hợp để viết thành chương trình; còn những năng lực nhiều chiều như tri giác, phong cách ngôn ngữ và chiến lược ngầm phải được đưa vào tham số mô hình. Hình 8-3 minh họa bốn phương thức này và mối quan hệ giữa chúng.

![Hình 8-3 Bốn phương thức cập nhật trong tiến hóa liên tục](images/fig8-3.svg)

Bảng 8-2 đưa ra một so sánh cô đọng. Bốn phương thức không loại trừ lẫn nhau: Agent ảnh y khoa dựa vào tham số để nhận diện tổn thương, dùng kho tri thức để cung cấp hướng dẫn mới nhất, rồi dùng mã để tính chỉ số rủi ro; giọng điệu tự nhiên của mô hình chăm sóc khách hàng đến từ hậu huấn luyện, chính sách doanh nghiệp cụ thể được cung cấp qua tri thức và Skill, còn tuân thủ trọng yếu được mã phía máy chủ bảo đảm.

Bảng 8-2 Phạm vi áp dụng của bốn phương thức tiến hóa liên tục

| Phương thức cập nhật | Phù hợp để chứa | Ưu điểm chính | Hạn chế chính |
|---|---|---|---|
| Kho tri thức kinh nghiệm | Sự kiện, quy luật kinh nghiệm, ngoại lệ và nguồn | Cập nhật nhanh, có thể truy vết, truy xuất theo nhu cầu | Phụ thuộc vào truy xuất và khả năng áp dụng đúng của mô hình |
| Prompt và Skills | Nguyên tắc phán đoán và quy phạm thao tác có thể ngôn ngữ hóa | Có thể giải thích, phạm vi tác động có thể kiểm soát | Dễ phình to, xung đột hoặc bị bỏ qua |
| Chương trình và Harness | Quy trình xác định, công cụ và ràng buộc cứng | Có thể kiểm thử, thực thi ổn định, chi phí thấp | Chi phí phát triển và bảo trì tương đối cao |
| Tham số mô hình | Tri giác nhiều chiều, phong cách sinh và chiến lược ngầm | Năng lực khái quát hóa mạnh, chi phí suy luận thấp | Chi phí cập nhật và hồi quy cao |

### Kết tinh kinh nghiệm thành tri thức

Phương thức tiến hóa nhẹ nhất là tổ chức những kinh nghiệm lặp đi lặp lại qua nhiều lần vận hành thành tài liệu tri thức có thể truy xuất. “Kho tri thức kinh nghiệm” ở đây chia sẻ công nghệ lưu trữ, lập chỉ mục và truy xuất với Chương 3, nhưng nguồn tri thức và mục tiêu xác minh khác nhau. Chương 3 chủ yếu trích xuất từ hội thoại người dùng, tài liệu và tập dữ liệu để trả lời “người dùng và thế giới có đặc điểm như thế nào”; chương này trích xuất từ quỹ đạo hành động và kết quả của Agent để trả lời “trong điều kiện nào nên làm gì”. Ví dụ, “hãng hàng không này yêu cầu đặt suất ăn đặc biệt trước hai mươi bốn giờ” là tri thức lĩnh vực; còn “trước khi đặt vé, hãy kiểm tra hạn chót đăng ký suất ăn đặc biệt để tránh thanh toán xong mới phát hiện không thể đáp ứng nhu cầu” là kinh nghiệm hành động.

Quỹ đạo gốc không phù hợp làm đơn vị tri thức chính thức. Nó vừa dài vừa nhiễu, chứa đầu ra thô của công cụ, các đường vòng ngẫu nhiên và chi tiết môi trường. Một hệ thống thận trọng hơn sẽ giữ lại ba tầng dữ liệu: quỹ đạo gốc bất biến dùng để kiểm toán; phân tích từng lần vận hành ghi lại thành công, thất bại và bài học ứng viên của lần đó; sau đó nhiều quỹ đạo cùng loại được so sánh, phân cụm và quy nạp để tạo thành tài liệu tri thức Markdown hướng đến tương lai. Tài liệu chính thức thường nêu rõ bối cảnh áp dụng, chiến lược đề xuất, hành vi bị cấm, điều kiện ngoại lệ, nguồn bằng chứng và thời điểm xác minh gần nhất, thay vì thuật lại toàn bộ quá trình của một nhiệm vụ cụ thể.

Thiết kế này có cùng tư tưởng hai giai đoạn với User-as-Code ở Chương 3. User-as-Code trước tiên nối thêm sự kiện hội thoại vào nhật ký bất biến, sau đó định kỳ tái dựng mô hình người dùng có cấu trúc; việc học từ kinh nghiệm cũng nên lưu bằng chứng trước rồi mới tạo tri thức khả biến ngoại tuyến. Hình 8-4 minh họa quá trình này. Việc tách ghi nhận khỏi tổ chức giúp tránh để một thành công ngẫu nhiên hoặc sự cố mạng lập tức thay đổi Agent, đồng thời cho phép hệ thống chỉ phán đoán điểm chung sau khi đã quan sát nhiều trường hợp thành công và thất bại.

![Hình 8-4 Từ quỹ đạo đã đánh giá đến tài liệu tri thức kinh nghiệm](images/fig8-4.svg)

Tài liệu kinh nghiệm không phải bản tóm tắt quỹ đạo đơn giản. Nội dung thực sự có giá trị chuyển giao đến từ đối chiếu: quỹ đạo thành công cùng loại đã làm gì, quỹ đạo thất bại thiếu điều gì; một chiến lược có hiệu quả trong những phiên bản môi trường nào và mất hiệu lực dưới những điều kiện tiên quyết nào. Chương 3 đã giới thiệu việc trích xuất, phân cụm và truy xuất tri thức nên chương này không lặp lại các thuật toán đó, mà tập trung vào cách đánh giá quỹ đạo trở thành điều kiện trích xuất và liệu tri thức được trích xuất có nâng cao hiệu quả của các nhiệm vụ sau hay không.

Học kinh nghiệm GAIA cung cấp một ví dụ trực quan. Sau khi Agent hoàn thành thành công một nhiệm vụ nhiều bước cần tìm kiếm, xử lý tệp và tính toán, hệ thống tổ chức quỹ đạo hành động thành bản tóm tắt chiến lược; khi nhiệm vụ mới xuất hiện, hệ thống truy xuất kinh nghiệm liên quan và đưa vào ngữ cảnh. Cách triển khai nghiêm ngặt hơn không chỉ lưu kinh nghiệm thành công mà còn giữ lại tri thức loại trừ từ các quỹ đạo thất bại, đồng thời ghi lại loại nhiệm vụ, điều kiện áp dụng và kết quả xác minh cho từng kinh nghiệm. Phản tư bằng ngôn ngữ tự nhiên do Reflexion[^reflexion-2023] đề xuất có thể tham gia tạo bài học ứng viên, nhưng bản thân phản tư không phải là bằng chứng; chỉ nội dung phù hợp với kết quả môi trường và thể hiện chuyển giao tích cực trong các nhiệm vụ sau mới nên được đưa vào tài liệu kinh nghiệm chính thức.

> **Thí nghiệm 8-2 ★★: Chắt lọc tài liệu tri thức kinh nghiệm từ quỹ đạo GAIA**
>
> Dự án `gaia-experience` ghi lại toàn bộ quỹ đạo của Agent trong các nhiệm vụ GAIA. Thí nghiệm này không trực tiếp truy xuất vector trên quỹ đạo, mà trước tiên dùng bộ xác minh kết quả nhiệm vụ để đánh dấu thành công, thất bại và thành công một phần, sau đó tổng hợp các quỹ đạo cùng loại theo năng lực cần thiết của nhiệm vụ. Mô-đun học tập so sánh các lộ trình thành công và thất bại, tạo tài liệu Markdown chứa điều kiện áp dụng, chiến lược then chốt, sai lầm thường gặp và quỹ đạo nguồn; ở giai đoạn áp dụng, hệ thống truy xuất các tài liệu này thay vì nạp quỹ đạo gốc. Đánh giá cần đồng thời báo cáo tỷ lệ thành công trên nhiệm vụ mới, chi phí truy xuất và chuyển giao tiêu cực do kinh nghiệm sai gây ra, đồng thời so sánh với hai đường cơ sở “không có kinh nghiệm” và “truy xuất trực tiếp bản tóm tắt quỹ đạo”.
>
> Phần triển khai đi kèm nằm tại [`gaia-experience`](../chapter8/gaia-experience/). `demo_documents.py` mặc định chạy ngoại tuyến; dùng `--extractor llm` để LLM thực đề xuất các ứng viên kinh nghiệm xuyên quỹ đạo.

[^reflexion-2023]: Shinn, N., et al. *Reflexion: Language Agents with Verbal Reinforcement Learning.* arXiv:2303.11366, 2023.

### Viết kinh nghiệm thành chỉ dẫn

Kho tri thức kinh nghiệm cung cấp tài liệu tham khảo cho Agent, còn Prompt và Skill có tính chỉ dẫn mạnh hơn. Khi nhiều quỹ đạo liên tục cho thấy cùng một loại sai lầm chiến lược và quy luật có thể được diễn đạt rõ bằng ngôn ngữ tự nhiên, hệ thống có thể nâng nó từ “kinh nghiệm có thể tham khảo” thành “quy tắc phải tuân thủ”. Quy tắc áp dụng cho gần như mọi nhiệm vụ phù hợp để đưa vào Prompt hệ thống; quy trình phức tạp chỉ có hiệu lực với một lĩnh vực, dự án hoặc công cụ cụ thể phù hợp hơn để viết thành Skill được nạp theo nhu cầu hoặc tệp chỉ dẫn dự án.

Học Prompt có phân công khác với kỹ thuật Prompt ở Chương 2. Chương 2 trả lời cách viết Prompt có cấu trúc rõ ràng và thân thiện với bộ nhớ đệm; ở đây trả lời loại phản hồi sản xuất nào đủ để kích hoạt sửa đổi Prompt và cách xác minh quy tắc mới trước khi triển khai. Việc sửa đổi cũng không nên thể hiện thành quá trình liên tục viết lại toàn bộ Prompt hệ thống. Cách đáng tin cậy hơn là tạo diff tối thiểu dựa trên một nhóm thất bại cùng loại, ghi rõ phạm vi tác dụng của quy tắc, kiểm tra xem nó có mâu thuẫn với quy tắc hiện có hay không, rồi đồng thời đánh giá trên các trường hợp biên đã kích hoạt thất bại và tập lưu giữ nhiệm vụ cũ.

Ví dụ, Agent chăm sóc khách hàng hàng không thường chuyển sang nhân viên quá sớm khi người dùng chất vấn chính sách. Đánh giá quỹ đạo cho thấy nó không vi phạm quy định, nhưng thiếu tính linh hoạt trong tuân thủ. Bản vá ứng viên có thể yêu cầu Agent trước tiên giải thích chính sách, nhận diện mục tiêu thực sự của người dùng và tìm phương án thay thế được phép; chỉ chuyển sang nhân viên khi người dùng yêu cầu rõ ràng hoặc vấn đề thực sự vượt quá quyền hạn. Nếu quy tắc mới giảm chuyển tiếp quá mức nhưng lại khiến các sự cố an toàn đáng lẽ phải chuyển cho con người tiếp tục được xử lý, thì nó chưa vượt qua hồi quy. Giá trị của việc học Prompt hệ thống không nằm ở tự động nối thêm nhiều văn bản, mà ở việc liên tục làm rõ phạm vi áp dụng của quy tắc bằng các trường hợp biên trong sản xuất.

Học Skill tuân theo cùng nguyên tắc nhưng có phạm vi tác động cục bộ hơn. Nếu nhiều kinh nghiệm cùng hình thành một quy trình yêu cầu bồi thường bảo hiểm hoàn chỉnh, hệ thống có thể tạo hoặc sửa Skill tương ứng. Những siêu năng lực như Skill Creator cho phép Agent tạo Skill, nhưng phần thực sự khó vẫn là lựa chọn bằng chứng, xử lý xung đột và xác minh hồi quy.

> **Thí nghiệm 8-3 ★★: Tối ưu Prompt hệ thống dựa trên quỹ đạo thất bại**
>
> Dự án `prompt-auto-optimization` sử dụng các trường hợp “chuyển tiếp quá mức” trong chăm sóc khách hàng hàng không. Thí nghiệm trước tiên dùng bộ xác minh quỹ đạo để nhận diện ba chiều: tuân thủ quy tắc, giải quyết nhiệm vụ và linh hoạt trong tuân thủ; sau đó để Coding Agent đọc Prompt hiện tại và tạo bản vá tối thiểu có giải thích nguồn gốc. Prompt ứng viên phải đồng thời vượt qua tập trường hợp biên và tập lưu giữ nhiệm vụ cũ; sau khi vượt qua, nó chỉ được kích hoạt canary dưới dạng phiên bản mới. Nhóm đối chứng sử dụng một lần tối ưu thủ công, rồi so sánh tốc độ giải quyết dạng thất bại mới, độ dài quy tắc và số lượng hồi quy giữa hai bên.
>
> Phần triển khai đi kèm nằm tại [`prompt-auto-optimization`](../chapter8/prompt-auto-optimization/). Kiểm thử ngoại tuyến bao quát ngưỡng chẩn đoán và phát hành, còn `--quick` sẽ thực sự gọi Agent thực hiện nhiệm vụ, LLM Judge và Coding Agent.

### Viết kinh nghiệm thành chương trình

Khi kinh nghiệm mô tả một thao tác ổn định, lặp lại và có thể xác minh, việc để mô hình đọc lại tài liệu và suy luận từ đầu mỗi lần không còn kinh tế. Khi đó, cách phù hợp hơn là biên dịch kinh nghiệm thành quy trình công việc, công cụ hoặc mã Harness để biến một lần khám phá thành chương trình có thể thực thi lặp lại. Chương 5 đã trình bày cách Coding Agent đọc và ghi tệp, chạy kiểm thử và tạo hệ thống; phần này không tập trung vào sinh mã nói chung, mà vào cách Agent sửa đổi phiên bản tương lai của chính nó dựa trên quỹ đạo của mình.

Đối tượng có thể sửa đổi không chỉ là công cụ mới. Tầng thao tác có thể biên dịch quỹ đạo trình duyệt thành quy trình công việc tham số hóa hoặc tạo bộ điều hợp cho API thay đổi; tầng điều khiển có thể sửa định tuyến công cụ, thử lại, ngắt mạch và chiến lược nén ngữ cảnh; tầng xác minh có thể bổ sung kiểm tra tham số, bộ xác minh trạng thái và kiểm thử hồi quy dựa trên thất bại trong sản xuất; tầng kiến trúc có thể thêm Reviewer Agent và thay đổi luồng thông tin giữa lập kế hoạch với thực thi.

Quy trình công việc trình duyệt cho thấy giá trị của kinh nghiệm được chương trình hóa. Khi gửi email lần đầu, Agent đa phương thức hoàn thành nhiệm vụ thông qua quan sát — suy nghĩ — hành động; sau đó hệ thống nhận diện các tham số khả biến và biên dịch hành động ổn định thành máy trạng thái. Việc phát lại không thể chỉ kiểm tra thao tác nhấp có được thực thi hay không, mà phải xác minh trạng thái trang thực trước mỗi bước và đặt lại môi trường để phát lại toàn bộ trước khi đưa vào kho. Thí nghiệm của PreAct[^preact] cho thấy các chương trình có điều kiện xác minh như vậy có thể tăng tốc đáng kể những nhiệm vụ lặp lại, còn xác minh trước khi lưu là chìa khóa ngăn chương trình sai làm ô nhiễm kho năng lực.

Khi môi trường thay đổi, chương trình cũng phải có khả năng mất hiệu lực. Không tìm thấy phần tử mục tiêu, API Schema thay đổi hoặc trạng thái cuối không thỏa mãn đều phải khiến quy trình công việc quay về trạng thái ứng viên, để Agent đầy đủ khám phá lại và tạo phiên bản mới, thay vì tiếp tục thực thi hoặc tuyên bố thành công. Việc tạo công cụ cũng là cùng một cơ chế: Alita[^alita-2025] bắt đầu từ một số ít năng lực cơ sở, tìm kiếm thư viện mã nguồn mở, đọc tài liệu, kiểm thử và đóng gói công cụ mới; sự tiến hóa thực sự không nằm ở việc “viết ra một đoạn mã”, mà ở chỗ công cụ mới sau khi được xác minh sẽ đi vào kho năng lực và có thể được tái sử dụng đúng trong các nhiệm vụ sau.

> **Thí nghiệm 8-4 ★★★: Tạo quy trình công việc có thể xác minh từ quỹ đạo trình duyệt**
>
> Sau khi Agent trong `browser-use-rpa` lần đầu hoàn thành nhiệm vụ web, hệ thống chắt lọc các hành động thành quy trình công việc có tham số và vị từ trạng thái, rồi chỉ đưa vào kho sau khi phát lại thành công trong môi trường đã đặt lại; khi trang thay đổi, hệ thống phải phát hiện mất hiệu lực và quay về học lại. Thí nghiệm lần lượt kiểm tra điều kiện tiên quyết của hành động, điều kiện hậu hành động và trạng thái cuối cùng của nhiệm vụ, đồng thời so sánh hai cách phán định: “chỉ xác nhận thao tác nhấp thành công” và “xác nhận trạng thái trang thực”.
>
> Phần triển khai đi kèm nằm tại [`browser-use-rpa`](../chapter8/browser-use-rpa/), đồng thời cung cấp bản trình diễn máy trạng thái xác định và lộ trình vận hành gọi Agent trình duyệt thực.

Việc Agent sửa mã của chính mình không có nghĩa là tiến trình đang chạy trực tiếp ghi đè lên bản thân. Hệ thống sản xuất nên tạo một nhánh ứng viên từ phiên bản ổn định hiện tại, để Coding Agent tạo bản vá tối thiểu, lần lượt vượt qua kiểm tra tĩnh, kiểm thử đơn vị, quét an toàn, phát lại quỹ đạo thất bại và hồi quy nhiệm vụ cũ, rồi mới tạo phiên bản mới có thể triển khai canary. Điều này chuyển “tự sửa đổi” thành một quy trình phát hành phần mềm có thể kiểm toán, đồng thời cũng là ranh giới giữa Chương 8 và Chương 5: Chương 5 cung cấp năng lực sửa đổi hệ thống, còn chương này cung cấp phương pháp tự sửa đổi được kích hoạt bởi kinh nghiệm và ràng buộc bằng vòng khép kín xác minh.

> **Thí nghiệm 8-5 ★★★: Kích hoạt Agent tự sửa đổi từ quỹ đạo thất bại**
>
> Với nhiều quỹ đạo có “cùng một lỗi không thể thử lại nhưng vẫn bị gọi liên tiếp”, mô-đun tiến hóa phải định vị nguyên nhân gốc ở mã thử lại và ngắt mạch, thay vì chỉ thêm một câu nhắc nhở trong Prompt. Coding Agent tạo bản vá ứng viên từ phiên bản ổn định; hệ thống lần lượt thực hiện kiểm tra tĩnh, phát lại quỹ đạo thất bại và hồi quy nhiệm vụ cũ. Sau khi xác minh thành công, bản vá chỉ được đưa vào canary; nếu thất bại thì từ chối phát hành và giữ lại phiên bản ổn định để khôi phục.
>
> Phần triển khai đi kèm nằm tại [`self-modifying-agent`](../chapter8/self-modifying-agent/), có thể chọn bộ sinh ứng viên xác định hoặc LLM Coding Agent thực; cả hai lộ trình dùng chung một ngưỡng phát hành.

[^preact]: Li, Bojie. *PreAct: Computer-Using Agents that Get Faster on Repeated Tasks.* arXiv:2606.17929, 2026.

[^alita-2025]: Qiu, J., et al. *Alita: Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution.* arXiv:2505.20286, 2025.

### Ghi kinh nghiệm vào tham số

Tri thức, chỉ dẫn và chương trình đều dựa trên một tiền đề: năng lực mục tiêu có thể được biểu đạt tương đối đầy đủ bằng ký hiệu bên ngoài. Tuy nhiên, những năng lực như hiểu ảnh y khoa, ngữ điệu giọng nói tự nhiên, loại bỏ “chất AI” khuôn mẫu trong văn bản và lập kế hoạch dài hạn rất khó nén thành vài quy tắc hoặc quy trình công việc. Những năng lực này phải được ghi vào tham số mô hình thông qua hậu huấn luyện.

Có tham số hóa hay không không chỉ do “nhiệm vụ có ổn định lâu dài hay không” quyết định. Độ lệch miền do thiết bị hình ảnh mới mang lại vẫn có thể cần LoRA hoặc tinh chỉnh liên tục; phong cách ngôn ngữ thay đổi nhanh cũng có thể thích nghi bằng huấn luyện ưu tiên định kỳ. Tính ổn định ảnh hưởng đến tần suất và chi phí cập nhật, nhưng tính chất biểu diễn của năng lực mới quyết định vật mang chính. Ngược lại, một quy tắc phê duyệt chuyển khoản ổn định lâu dài cũng không nên chỉ dựa vào trí nhớ tham số; mã phía máy chủ vẫn phải cung cấp bảo đảm xác định.

Chương 7 đã thảo luận đầy đủ về SFT, chưng cất và RL nên phần này không lặp lại thuật toán. Đối với tiến hóa liên tục, điều then chốt là chuyển các quỹ đạo sản xuất đã được đánh giá thành dữ liệu huấn luyện: bản minh họa chất lượng cao có thể đi vào SFT, ưu tiên rõ ràng có thể tạo thành dữ liệu theo cặp, còn tương tác có phần thưởng môi trường đáng tin cậy có thể dùng cho RL. Trước khi đưa vào huấn luyện, vẫn cần loại bỏ thông tin riêng tư, lọc quỹ đạo sai và giữ lại tập hồi quy độc lập; sau huấn luyện, cần kiểm tra xem năng lực tổng quát và căn chỉnh an toàn có bị quên hay không.

Học tham số thường phối hợp với các phương pháp bên ngoài. Mô hình ảnh y khoa dùng tham số để học biểu diễn thị giác, dùng kho tri thức cung cấp hướng dẫn mới nhất, dùng mã để đo tổn thương và tính rủi ro; giọng điệu tự nhiên của dịch vụ khách hàng có thể được định hình ở cấp phân phối tổng thể bằng huấn luyện ưu tiên, sau đó dùng Prompt quy định nhận diện thương hiệu hiện tại và dùng bộ nhớ người dùng để thích nghi với sở thích giao tiếp cá nhân. Tiến hóa liên tục không phải là chọn một đáp án duy nhất trong bốn phương thức, mà là đặt từng năng lực vào vị trí phù hợp nhất để biểu đạt và quản trị nó.

## Xây dựng vòng khép kín tiến hóa liên tục có thể vận hành dài hạn

Chỉ khi đi vào cùng một chu trình có kiểm soát, bốn phương thức cập nhật mới chuyển từ tối ưu một lần thành tiến hóa liên tục. Hình 8-5 trình bày cấu trúc hai vòng thận trọng hơn trong hệ thống sản xuất: vòng thực thi trực tuyến chỉ hoàn thành nhiệm vụ và ghi lại bằng chứng, không trực tiếp viết lại Agent chính thức; vòng tiến hóa ngoại tuyến tổng hợp quỹ đạo, chẩn đoán nguyên nhân gốc, tạo sửa đổi ứng viên, rồi phát hành phiên bản mới sau khi vượt qua ngưỡng xác minh. Hai vòng được kết nối bằng kho kinh nghiệm và tập đánh giá có phiên bản.

![Hình 8-5 Hai vòng thực thi trực tuyến và tiến hóa ngoại tuyến](images/fig8-5.svg)

Voyager[^voyager-2023] minh họa một vòng tiến hóa liên tục tương đối hoàn chỉnh. Trong Minecraft, nó lựa chọn mục tiêu mới dựa trên năng lực hiện tại, lặp chương trình theo phản hồi môi trường, lưu mã vào kho kỹ năng sau khi xác minh thành công, rồi kết hợp các kỹ năng cũ để giải quyết nhiệm vụ khó hơn. Chương trình học tự động, kỹ năng có thể thực thi và xác minh môi trường đều không thể thiếu: chỉ có kho kỹ năng mà không có chương trình học thì Agent không biết bước tiếp theo nên học gì; chỉ có tự phản tư mà không có xác minh môi trường thì kho kỹ năng sẽ tích lũy sai sót; chỉ có khám phá mà không có lưu giữ lâu dài thì mỗi nhiệm vụ vẫn phải bắt đầu lại từ đầu. Dù tri thức, Prompt, công cụ và tham số của Agent thực tế phức tạp hơn, quá trình học cơ bản vẫn tương tự.

### Từ định vị vấn đề đến kết tinh kinh nghiệm

Cùng một vấn đề bề mặt có thể cần những cách sửa đổi khác nhau. Hiện tượng Agent chăm sóc khách hàng bịa đặt sự kiện có thể do kho tri thức thiếu thông tin, cũng có thể do Prompt không yêu cầu trích dẫn; khi chưa hoàn thành nhiệm vụ mà Agent đã đưa ra cam kết sai sự thật rằng “đã hoàn thành”, vấn đề có thể được sửa bằng chỉ dẫn hoặc Harness có thể cưỡng chế kiểm tra phản hồi so với trạng thái công cụ. Mô-đun tiến hóa trước tiên phải định vị nguyên nhân gốc, sau đó chọn đối tượng sửa đổi tối thiểu, dễ xác minh và dễ khôi phục nhất. Sự cố ngẫu nhiên thiếu bằng chứng không nên lập tức kích hoạt học tập mà cần tiếp tục tích lũy mẫu.

Lựa chọn này cũng có thể thay đổi khi kinh nghiệm tăng lên. Một chiến lược mới được phát hiện trước tiên được cung cấp để truy xuất dưới dạng tài liệu kinh nghiệm; sau khi được nhiều trường hợp xác minh lặp lại, nó có thể được nâng thành tri thức. Tri thức có ba cách biểu đạt: quy tắc có thể mô tả rõ bằng ngôn ngữ tự nhiên có thể được kết tinh thành Skill; nếu các bước ổn định và không cần năng lực hiểu ngôn ngữ tự nhiên thì có thể được biên dịch thành mã công cụ; nếu thực chất nó phản ánh năng lực quyết định ngầm có phạm vi rộng thì có thể đi vào hậu huấn luyện.

### Xác minh, phát hành và khôi phục

Mọi sửa đổi trước tiên đều tạo năng lực ứng viên hoặc Agent ứng viên, thay vì trực tiếp ghi đè phiên bản sản xuất. Tài liệu tri thức phải được xác minh xem sau khi truy xuất có nâng cao hiệu quả nhiệm vụ mới hay không; Prompt và Skill phải được kiểm tra trên trường hợp biên và hồi quy nhiệm vụ cũ; chương trình phải chạy kiểm thử trong sandbox và môi trường đã đặt lại; cập nhật tham số phải được kiểm tra về quên, an toàn và nhiệm vụ ngoài phân phối. Sau khi vượt qua xác minh, phiên bản vẫn phải được phát hành canary để quan sát lưu lượng thực; khi các chỉ số trọng yếu suy giảm, hệ thống tự động khôi phục về phiên bản an toàn đã biết.

Đánh giá không phải kỳ thi sau khi học xong, mà là một phần không thể thiếu của quá trình tự tiến hóa. Đánh giá dài hạn tối thiểu phải đồng thời quan sát bốn loại kết quả:

- hồi quy (regression), tức kinh nghiệm mới có xung đột với những kinh nghiệm hiện có khác hay không và các trường hợp vốn vượt qua trước đây có bị hồi quy hay không;
- năng lực khái quát hóa, tức mức cải thiện mà kinh nghiệm mới mang lại trong những bối cảnh chưa được tập kiểm thử bao phủ;
- hiệu quả Token, tức chi phí token tiêu thụ để hoàn thành nhiệm vụ;
- tính an toàn, tức quy tắc, quyền riêng tư và ranh giới từ chối có trôi dạt theo quá trình tiến hóa hay không.

Một vấn đề chỉ giải quyết được trường hợp thất bại hiện tại nhưng suy giảm ở những trường hợp hiện có khác hoặc lĩnh vực mới không phải là học liên tục thành công.

### Hợp nhất, quên và duy trì năng lực

Tiến hóa liên tục cũng không có nghĩa là để tri thức, Prompt và công cụ tăng trưởng vô hạn. Sự suy thoái ngữ cảnh được đề cập ở Chương 2 sẽ tái xuất hiện trên thang thời gian dài hơn: tài liệu kinh nghiệm xung đột lẫn nhau, Prompt bị nhấn chìm trong các quy tắc biên, kho Skill xuất hiện năng lực trùng lặp, nhiều lần tinh chỉnh gây quên thảm họa. Hệ thống cần định kỳ tổ chức ngoại tuyến:

- hợp nhất kinh nghiệm trùng lặp, giữ lại nguồn và phiên bản;
- chuyển quy tắc cục bộ từ Prompt toàn cục sang Skill lĩnh vực để giữ Prompt toàn cục gọn gàng;
- duy trì cấu trúc rõ ràng cho Prompt và Skill, giống một cuốn sổ hướng dẫn dành cho nhân viên mới, tránh liệt kê quy tắc theo kiểu “99 điều quân luật”;
- xác minh lại các công cụ lâu ngày không được sử dụng;
- xóa tri thức bị bằng chứng mới bác bỏ;
- huấn luyện lại LoRA từ mô hình nền tảng gốc.

> **Thí nghiệm 8-6 ★★★: Đánh giá Agent có đang tiến hóa liên tục hay không**
>
> Xây dựng một luồng nhiệm vụ theo nhiều giai đoạn thay vì chạy lặp lại cùng một nhóm nhiệm vụ. Giai đoạn đầu cung cấp một số nhiệm vụ có chung quy luật tiềm ẩn để Agent tạo tài liệu kinh nghiệm hoặc sửa đổi ứng viên; giai đoạn hai kiểm tra xem các quy luật này có thể chuyển giao sang cách diễn đạt và môi trường khác hay không; giai đoạn ba đưa vào thay đổi quy tắc, yêu cầu hệ thống cập nhật hoặc loại bỏ năng lực cũ; giai đoạn bốn kiểm thử lại các nhiệm vụ ở giai đoạn đầu để đo mức độ quên. Báo cáo phải đồng thời bao gồm đường cong học tập, tỷ lệ duy trì năng lực cũ, thay đổi chi phí và Rubric an toàn. Thí nghiệm này có thể tái sử dụng nhiệm vụ và khung xác minh của `self-evolution-eval`, nhưng đối tượng đánh giá được mở rộng từ một lần tạo công cụ sang toàn bộ quá trình cập nhật dài hạn.
>
> Phần triển khai đi kèm nằm tại [`self-evolution-eval`](../chapter8/self-evolution-eval/), mặc định so sánh ba Agent tham chiếu: có thể cập nhật, chỉ nối thêm và tĩnh; dùng `--profile llm` để LLM thực trải qua cùng một luồng nhiệm vụ dài hạn.

[^voyager-2023]: Wang, G., et al. *Voyager: An Open-Ended Embodied Agent with Large Language Models.* arXiv:2305.16291, 2023.

## Tổng kết chương

Học liên tục đang trở thành một trong những năng lực quan trọng nhất của Agent, nhưng các mô hình hiện nay vẫn chưa thể tự mình thực hiện học liên tục đáng tin cậy. Sự thích nghi ngữ cảnh trong lúc suy luận không tự động được lưu giữ lâu dài, còn cập nhật tham số trực tuyến chưa qua xác minh sẽ khuếch đại nhiễu, tấn công và trôi dạt năng lực. Vì vậy, con đường khả thi ở giai đoạn hiện tại là xây dựng một hệ thống học tập có kiểm soát bao quanh mô hình.

Các nhiệm vụ có kết quả rõ ràng nên tận dụng tối đa môi trường và mã để xác minh; các nhiệm vụ mở cần đưa những chiều như tuân thủ quy tắc, độ tin cậy thực tế, tính nhất quán giữa cam kết và hành động, chất lượng diễn đạt và linh hoạt trong tuân thủ vào Rubric. Đánh giá đa chiều giữ lại bản chất thất bại và bằng chứng, từ đó mới hỗ trợ được chẩn đoán về sau.

Sau khi thu được tín hiệu học tập, vị trí cập nhật phụ thuộc vào tính chất biểu diễn của năng lực: kinh nghiệm và sự kiện được kết tinh thành tài liệu tri thức; chiến lược có thể mô tả rõ bằng ngôn ngữ được viết vào Prompt hoặc Skill; quy trình và ràng buộc xác định được viết thành chương trình và Harness; phong cách cùng chiến lược khó diễn đạt bằng ngôn ngữ được đưa vào tham số mô hình. Bốn phương thức bổ trợ lẫn nhau, không phương thức nào có thể thay thế ba phương thức còn lại.

“Học liên tục” thực sự đến từ tương tác liên tục giữa Agent với môi trường: ghi bằng chứng trực tuyến, tạo sửa đổi ứng viên ngoại tuyến, phát hành canary sau khi vượt qua xác minh hồi quy và an toàn, rồi hợp nhất, loại bỏ và khôi phục trong quá trình vận hành dài hạn. Khi năng lực học của bản thân mô hình được nâng cao, một phần các cơ chế ngoại vi này có thể dần được nội hóa; nhưng trước thời điểm đó, chúng giúp Agent không còn chỉ lặp lại việc gọi một mô hình đóng băng, mà có thể từng bước hình thành một hệ thống năng lực có thể xác minh, truy vết và sửa chữa.

## Câu hỏi suy ngẫm

1. ★★ Một tài liệu kinh nghiệm được ba quỹ đạo thành công và một quỹ đạo thất bại hỗ trợ. Thất bại xảy ra trên phiên bản API mới hơn. Hệ thống nên xác định đây là kinh nghiệm đã bị bác bỏ hay điều kiện áp dụng đã thay đổi như thế nào?
2. ★★ Mức độ hài lòng của người dùng với Agent chăm sóc khách hàng tăng lên, nhưng tỷ lệ vi phạm quy tắc cũng tăng. Tại sao không thể dùng mức độ hài lòng làm tín hiệu học tập duy nhất? Bạn sẽ thiết kế các chỉ số rào chắn như thế nào?
3. ★★★ Cùng một vấn đề “cam kết sai sự thật” có thể được giảm nhẹ bằng Prompt, kiểm tra Harness hoặc huấn luyện tham số. Bạn sẽ dựa trên những bằng chứng nào để chọn vị trí sửa đổi?
4. ★★★ Agent có thể sửa đổi công cụ và bộ xác minh, nhưng không nên sửa đổi gốc tin cậy phê duyệt cập nhật của chính nó. Bạn sẽ phân chia quyền hạn và ranh giới mã giữa hai phần này như thế nào?
5. ★★ Sau khi kho tri thức kinh nghiệm liên tục tăng trưởng, lỗi truy xuất và xung đột tri thức sẽ triệt tiêu lợi ích học tập. Nên thiết kế cơ chế phiên bản, thời hiệu và loại bỏ như thế nào?
6. ★★★ Học tham số giỏi xử lý phong cách ngôn ngữ tự nhiên nhưng khó bảo đảm quy tắc nghiệp vụ cứng. Hãy thiết kế cho dịch vụ chăm sóc khách hàng y tế một phương án tiến hóa liên tục phối hợp giữa tham số, tri thức, Skill và ràng buộc bằng mã.
