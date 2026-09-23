# YoutubePlus cho NVDA

> YoutubePlus là add-on dành cho những người thích dùng YouTube nhưng thấy nhiều tính năng trên trang web khó tiếp cận, chẳng hạn như đọc bình luận của video.
> Chúng tôi đưa những tính năng này đến với bạn ngay trong giao diện của NVDA. Giao diện dễ điều hướng, hỗ trợ phím tắt và tùy chỉnh được hoàn toàn. Bạn không cần lo về khóa API hay phải liên kết bất kỳ tài khoản cá nhân nào với add-on.
> Bạn có thể theo dõi các kênh yêu thích và yên tâm rằng sẽ thấy mọi video của những kênh đó, không bị thuật toán của YouTube lọc mất.
> Add-on cũng có hệ thống Yêu thích (Favorites) cho video, kênh và danh sách phát, cùng với Danh sách xem sau (Watch List) để lưu những nội dung bạn quan tâm nhưng chưa có thời gian xem.
> Add-on có sẵn chức năng tìm kiếm video, hiển thị kết quả ngay trong giao diện quen thuộc của add-on, không chỉ là một ô tìm kiếm rồi mở YouTube trong trình duyệt.
> Add-on còn có tính năng tải xuống để lưu video hoặc file âm thanh, nhưng đây chỉ là tiện ích đi kèm chứ không phải trọng tâm. Nếu bạn chủ yếu cần tải xuống, hãy tìm hiểu các add-on chuyên dụng cho việc này.
> Điều duy nhất add-on này không làm là nhúng trình phát video. Chúng tôi cho rằng trình phát web của YouTube tự nó đã đủ dễ tiếp cận. Nếu bạn vẫn thấy chưa đủ, có thể dùng các add-on khác như [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) để cải thiện trải nghiệm.

## Phím tắt và các lệnh

Add-on này dùng hệ thống phím tắt theo lớp (layer) để tránh xung đột với các add-on khác hoặc các lệnh của NVDA.
Nhấn **NVDA+Y** để vào chế độ lệnh của YoutubePlus, sau đó nhấn một trong các phím dưới đây để mở từng tính năng hoặc cửa sổ.

**Lưu ý:** Nếu phím tắt chính (`NVDA+Y`) bị xung đột với add-on khác, bạn có thể đổi nó tại `NVDA -> Tùy chọn (Preferences) -> Cử chỉ nhập (Input Gestures)...`, trong nhóm "YoutubePlus".

### Các phím dùng được trong lớp YoutubePlus

* a: (thêm vào...): mở menu con để bạn chọn nơi thêm video hoặc kênh hiện tại
* f: (mở video yêu thích): mở cửa sổ video yêu thích
* c: (mở kênh yêu thích): mở cửa sổ kênh yêu thích
* p: (mở danh sách phát yêu thích): mở cửa sổ danh sách phát yêu thích
* w: (hiện danh sách xem sau): mở cửa sổ Danh sách xem sau
* d: (tải xuống): hỏi bạn muốn tải cả video hay chỉ tải âm thanh
* e: (tìm kiếm): mở cửa sổ tìm kiếm video
* q: (tìm nhanh): tìm trên YouTube ngay lập tức bằng đoạn văn bản đang chọn, hoặc bằng nội dung trong clipboard nếu bạn chưa chọn gì, mà không cần mở hộp thoại tìm kiếm trước
* control+h: (lịch sử tìm kiếm): mở cửa sổ Yêu thích ngay tại thẻ Lịch sử tìm kiếm (Search History)
* i: (thông tin): mở cửa sổ chi tiết video
* t: (hiện mốc thời gian): hiển thị các mốc thời gian hoặc chương (chapter) nếu có
* g: (mô tả ảnh thu nhỏ): tải ảnh thu nhỏ (thumbnail) của video rồi gửi cho ứng dụng Be My Eyes để nhận mô tả trực tiếp
* m: (mở quản lý đăng ký): mở cửa sổ quản lý các kênh đã đăng ký
* s: (mở nguồn cấp đăng ký): hiển thị video từ các kênh bạn đang theo dõi
* u: (mở Trình quản lý hồ sơ người dùng): mở cửa sổ quản lý hồ sơ người dùng
* l: (xem bình luận): hiển thị bình luận (chi tiết ở phần sau)
* shift+l: (dừng theo dõi live chat): dừng theo dõi live chat (trò chuyện trực tiếp)
* r: (bật/tắt tự động đọc live chat): bật hoặc tắt việc tự động đọc to các tin nhắn live chat mới
* v: (hiện live chat): mở lại cửa sổ live chat nếu bạn lỡ đóng nó trong khi buổi phát trực tiếp vẫn đang diễn ra
* y: (mở hộp thoại cài đặt YoutubePlus): mở nhanh phần cài đặt của NVDA và chuyển tiêu điểm đến nhóm YoutubePlus
* h: (trợ giúp): mở cửa sổ liệt kê tất cả các phím tắt hiện có

**Lưu ý:** Với các lệnh tác động trực tiếp lên video, add-on sẽ kiểm tra cửa sổ trình duyệt bạn đang mở trước. Nếu đang mở trang video YouTube, nó dùng URL của video đó. Nếu không có trang video nào đang mở, nó sẽ kiểm tra clipboard xem có URL YouTube hay không.

## Chi tiết các tính năng và lệnh

### a: (thêm vào...)

Lệnh này trong lớp YoutubePlus gửi thông tin video hoặc kênh đến nơi bạn chọn:

* Thêm vào Video yêu thích (Add to Favorite Videos) (v)
* Thêm vào Kênh yêu thích (Add to Favorite Channels) (c)
* Thêm vào Danh sách phát yêu thích (Add to Favorite Playlist) (p)
* Đăng ký kênh (Subscribe to Channel) (s)
* Thêm vào Danh sách xem sau (Add to Watch List) (w)

Add-on kiểm tra trang trình duyệt đang mở trước. Nếu đó là trang video YouTube, add-on lấy URL và xử lý theo lựa chọn của bạn. Nếu trang đó không phải video YouTube, hoặc không có trình duyệt nào đang mở, add-on sẽ kiểm tra clipboard xem có URL YouTube hay không.

Hầu hết các lệnh đều dùng được với mọi loại URL YouTube, vì add-on có thể tự suy ra thông tin cần thiết. Ví dụ, nếu bạn đang ở trang video và chọn "Thêm vào Kênh yêu thích", add-on tự lấy được URL của kênh. Việc đăng ký kênh cũng hoạt động tương tự.

Ngoại lệ duy nhất là danh sách phát: bạn phải đang mở một trang danh sách phát YouTube, hoặc đã sao chép một URL danh sách phát YouTube hợp lệ vào clipboard.

### d: (tải video/âm thanh)

Lệnh này mở một hộp thoại nhỏ hỏi bạn muốn tải video hay chỉ tải âm thanh. Bạn có thể chọn thư mục lưu file và tinh chỉnh chất lượng/định dạng trong phần [Cài đặt](#cài-đặt).

**Tải video cần có FFmpeg.** YouTube hiện không còn phát hầu hết video dưới dạng một file gộp sẵn cả hình lẫn tiếng, nên cần FFmpeg để ghép các luồng riêng biệt lại. YoutubePlus không đóng gói sẵn FFmpeg (để tránh làm phình thư mục cấu hình NVDA của mỗi người dùng). Nếu khi tải video mà không tìm thấy FFmpeg trên máy, và công cụ `winget` của Windows có sẵn, YoutubePlus sẽ đề nghị tự cài FFmpeg giúp bạn bằng một câu hỏi Có/Không. Cài xong, quá trình tải tiếp tục tự động, không cần khởi động lại NVDA. Nếu máy không có cả FFmpeg lẫn `winget`, add-on sẽ báo cho bạn biết và hủy việc tải một cách gọn gàng.

Theo mặc định, tải riêng âm thanh không cần FFmpeg. Chỉ khi bạn chọn một định dạng âm thanh khác "Best available (no conversion)" (Tốt nhất hiện có, không chuyển đổi) trong phần cài đặt nâng cao bên dưới thì mới cần FFmpeg, vì việc chuyển sang định dạng âm thanh khác cũng phải qua FFmpeg.

Lưu ý: tính năng tải xuống chỉ mang tính tiện ích và có thể bị hạn chế nếu dùng nhiều. Nếu bạn cần tải số lượng lớn nội dung YouTube, nên dùng các công cụ chuyên dụng khác.

### e: (tìm kiếm)

Lệnh này mở cửa sổ tìm kiếm YouTube. Gõ từ khóa vào ô tìm kiếm rồi nhấn Enter để tìm ngay. Bạn cũng có thể nhấn Tab để chỉnh số lượng kết quả hiển thị. Add-on sẽ nhớ giá trị này cho các lần tìm sau.

Ô tìm kiếm là một combo box ghi nhớ các lần tìm trước: nhấn mũi tên Xuống (hoặc Alt+Xuống) để mở danh sách các từ khóa đã tìm và chọn một từ khóa thay vì gõ lại.

Bên dưới ô từ khóa có bốn bộ lọc để thu hẹp kết quả, và bạn có thể kết hợp tự do các bộ lọc này (ví dụ: danh sách phát đăng trong tháng này, sắp xếp theo lượt xem):

* **Content type:** Videos (mặc định), Channels hoặc Playlists
* **Duration:** Any, Short (dưới 4 phút), Medium (4-20 phút) hoặc Long (trên 20 phút)
* **Upload date:** Any, Past hour, Today, This week, This month hoặc This year
* **Sort by:** Relevance (mặc định), Upload date hoặc View count

Kết quả hiển thị theo cùng định dạng [danh sách video](#danh-sách-video) được dùng xuyên suốt add-on, chứ không phải một trang web YouTube. Một kết quả loại Channels sẽ mở/sao chép URL kênh và hiện menu Action rút gọn (không có tải xuống, bình luận, hay các hành động chỉ dành riêng cho video); một kết quả loại Playlists sẽ mở rộng thành danh sách video riêng của nó, giống như một danh sách phát yêu thích.

#### Tìm kiếm trong một kênh

Ô **Within channel** giới hạn việc tìm kiếm chỉ trong các video của một kênh, thay vì toàn bộ YouTube. Khi ô này có giá trị, bốn bộ lọc ở trên không áp dụng được cho trang tìm kiếm riêng của kênh nên sẽ bị ẩn đi.

Bắt đầu gõ tên kênh, một danh sách thả xuống sẽ gợi ý các kênh từ Lịch sử tìm kiếm, Kênh yêu thích, và Kênh đã đăng ký của bạn. Nếu những gì bạn gõ không khớp với bất kỳ mục nào trong số đó (ví dụ: một kênh bạn chưa từng tìm hay thêm vào yêu thích trước đây), add-on sẽ tìm kênh đó trên YouTube và hiện danh sách để bạn xác nhận đúng kênh mình muốn — add-on sẽ không bao giờ tự đoán ngầm. Bạn cũng có thể dán trực tiếp URL của kênh thay vì gõ tên.

Bạn cũng có thể mở hộp thoại này với kênh đã được điền sẵn: từ thẻ Channel trong cửa sổ Yêu thích, chọn một kênh rồi nhấn nút **Search in this channel...**.

#### q: (tìm nhanh)

Đây là cách nhanh hơn hộp thoại tìm kiếm ở trên. Chọn một đoạn văn bản trong bất kỳ ứng dụng nào (hoặc sao chép từ khóa vào clipboard nếu bạn không chọn gì), rồi nhấn Q trong lớp YoutubePlus. Add-on sẽ tìm ngay trên YouTube bằng đoạn văn bản đó, với số lượng kết quả đã lưu từ lần tìm gần nhất. Không cần hộp thoại, không phải nhấn thêm phím nào.

#### Lịch sử tìm kiếm (Search History)

Mọi lần tìm kiếm của bạn, dù từ hộp thoại tìm kiếm hay tìm nhanh, đều được lưu tự động, cùng với các bộ lọc đã dùng (kể cả kênh được đặt qua "Within channel"). Nhấn **Control+H** trong lớp YoutubePlus để chuyển thẳng đến thẻ Lịch sử tìm kiếm trong cửa sổ Yêu thích. Tại đây bạn có thể:

* Nhấn Enter, hoặc nút **Search Again** (Tìm lại), để chạy lại một lần tìm trước đó với đúng các bộ lọc đã dùng (hoặc đúng kênh cũ, nếu là tìm kiếm giới hạn trong một kênh) — một mục tìm kiếm giới hạn trong kênh sẽ hiển thị trong danh sách dưới dạng "từ khóa (in Tên kênh)" để bạn nhận ra ngay
* Nhấn **New Search (Alt+N)** (Tìm kiếm mới) để mở hộp thoại tìm kiếm
* Nhấn Delete, hoặc nút **Remove** (Xóa), để xóa một mục
* Nhấn nút **Clear All** (Xóa tất cả) để xóa toàn bộ lịch sử

### i: (thông tin video)

Hiển thị các thông tin sau về video hiện tại:

* Tiêu đề (Title)
* Kênh (Channel)
* Thời lượng (Duration)
* Ngày đăng (Uploaded)
* Lượt xem (Views)
* Lượt thích (Likes)
* Số bình luận (Comments)
* Mô tả (Description)

### t: (mốc thời gian / chương)

Hiển thị danh sách mốc thời gian hoặc chương của video (nếu người tạo video có cung cấp). Nếu add-on thông báo "No chapters found in this video" (Không tìm thấy chương nào trong video này), nghĩa là video đó đơn giản là không có dữ liệu chương.

Cửa sổ này tiện hơn so với đọc chương trên trình duyệt:

* Có ô tìm kiếm để lọc danh sách mốc thời gian/chương. Kết quả cập nhật ngay, không cần nhấn Enter
* Danh sách đầy đủ hiển thị phần mô tả của từng mục trước, rồi đến vị trí thời gian
* Có vùng văn bản chỉ đọc để đọc các mô tả chương dài
* Có nút "Open Chapter" (Mở chương), hoặc nhấn Space hay Enter, để nhảy thẳng đến chương đó trong video
* Nút Copy Title (Alt+C) để sao chép tên chương
* Nút Copy URL (Alt+U) để sao chép URL kèm mốc thời gian của chương đó
* Nút Export (Alt+E) để lưu toàn bộ dữ liệu mốc thời gian/chương thành file văn bản

### g: (mô tả ảnh thu nhỏ)

Tải một ảnh thu nhỏ và gửi cho ứng dụng **Be My Eyes** để nhận mô tả trực tiếp, mà không phải rời khỏi NVDA. Lệnh này nhận biết ngữ cảnh: nó mô tả ảnh thu nhỏ của video khi bạn đang ở trang video, ảnh đại diện của kênh khi bạn đang ở trang kênh, và ảnh bìa của danh sách phát khi bạn đang ở trang danh sách phát. Thứ tự nhận diện URL giống mọi lệnh khác (cửa sổ trình duyệt đang mở trước, rồi đến clipboard). Lệnh này cũng có trong menu Hành động (Action) của video (chỉ với ảnh thu nhỏ video) và có thể đặt làm Hành động nhanh (Quick Action) cho phím Space.

Add-on luôn chọn ảnh có độ phân giải cao nhất mà yt-dlp cung cấp, nên file gửi cho Be My Eyes là bản tốt nhất có thể.

Bạn cũng có thể mô tả ảnh đại diện của kênh hoặc ảnh bìa của danh sách phát ngay từ cửa sổ Yêu thích, không cần mở trang đó ở đâu cả. Xem các nút **Describe Avatar** (Mô tả ảnh đại diện) và **Describe Cover** (Mô tả ảnh bìa) trong phần [Yêu thích](#yêu-thích-favorites) bên dưới.

**Lưu ý:** Tính năng này yêu cầu bạn tự cài ứng dụng [Be My Eyes](https://www.bemyeyes.com/) trên máy, vì add-on không cài đặt hay đóng gói kèm ứng dụng này. Nếu chưa cài, YoutubePlus sẽ đề nghị mở trang Microsoft Store của ứng dụng để bạn cài ngay.

### Yêu thích (Favorites)

Cửa sổ hiển thị các mục bạn đã lưu, chia thành 5 thẻ theo loại:

* **Video:** Liệt kê các video đã lưu, được sắp xếp vào những danh mục do bạn tự tạo. Cây danh mục nằm bên trái, danh sách video của danh mục đang chọn nằm bên phải (xem phần [Danh mục](#danh-mục-thẻ-video-và-watch-list) bên dưới). Mỗi mục đều có nút Action (Hành động) và Copy (Sao chép), mô tả ở dưới.
* **Channel (Kênh):** Liệt kê các kênh đã lưu, kèm khung mô tả kênh. Có các nút để mở kênh, duyệt nội dung của kênh theo loại, tìm kiếm trong kênh, và mô tả ảnh đại diện qua Be My Eyes (Alt+D).
* **Playlist (Danh sách phát):** Liệt kê các danh sách phát đã lưu. Nhấn Space, Enter hoặc Alt+V để mở rộng và xem tất cả video trong một danh sách phát. Có nút Open on Web (Mở trên web) (Alt+W) và nút Describe Cover (Mô tả ảnh bìa) (Alt+D) để nhận mô tả của ảnh bìa danh sách phát từ Be My Eyes.
* **Watch List (Danh sách xem sau):** Liệt kê các video đã lưu theo cùng bố cục (cây danh mục + danh sách) với thẻ Video, nhưng có bộ danh mục độc lập riêng.
* **Search History (Lịch sử tìm kiếm):** Liệt kê mọi lần tìm kiếm bạn đã thực hiện, với các lựa chọn tìm lại, xóa từng mục hoặc xóa toàn bộ (xem phần [Lịch sử tìm kiếm](#lịch-sử-tìm-kiếm-search-history) ở trên).

#### Các lệnh trong cửa sổ Yêu thích

* Nhấn Control+1 đến Control+5 để chuyển giữa các thẻ
* Nhấn Control+Lên/Xuống để đổi thứ tự các thẻ
* Nhấn Control+C (sao chép), Control+X (cắt) hoặc Control+V (dán) để sắp xếp lại thứ tự các mục
    * Video yêu thích và Danh sách xem sau hỗ trợ sao chép và di chuyển mục qua lại giữa hai thẻ, kể cả các mục nằm trong danh mục. Thẻ Video và thẻ Watch List mỗi thẻ có danh sách danh mục riêng, nên khi một mục được chuyển giữa hai thẻ, nó sẽ được đặt vào danh mục đang chọn ở thẻ đích. Kênh yêu thích và Danh sách phát yêu thích chỉ hỗ trợ di chuyển mục trong phạm vi danh sách của chính nó.
* Nhấn Alt+R hoặc Delete để xóa một mục
* Nhấn Alt+N để thêm một mục mới từ clipboard. Với thẻ kênh và thẻ danh sách phát, URL phải đúng loại của thẻ đó
* Nhấn **Alt+O (Sort...)** (Sắp xếp...) để mở hộp thoại sắp xếp cho thẻ hiện tại, xem phần [Sắp xếp](#sắp-xếp-sorting) bên dưới
* Ô tìm kiếm lọc kết quả ngay khi bạn gõ, không cần nhấn Enter

#### Danh mục (thẻ Video và Watch List)

Cả thẻ Video và thẻ Watch List đều cho phép bạn tự tổ chức các mục vào danh mục, dùng một cây thư mục bên trái tách biệt với danh sách mục bên phải. Mỗi thẻ có danh mục riêng, nên tạo danh mục ở thẻ này không ảnh hưởng đến thẻ kia. Luôn có sẵn một nút mặc định cho các mục chưa phân loại ("Videos" ở thẻ Video, "Watch List" ở thẻ Watch List).

Khi tiêu điểm đang ở cây danh mục:

* Nhấn **Control+=** để thêm danh mục mới
* Nhấn **F2** để đổi tên danh mục đang chọn
* Nhấn **Delete** để xóa danh mục đang chọn. Nếu danh mục còn chứa mục, bạn sẽ được hỏi muốn chuyển chúng về nút mặc định hay xóa cùng danh mục
* Nhấn **Control+Shift+Lên** / **Control+Shift+Xuống** để đổi thứ tự danh mục đang chọn
* Nhấn Enter, hoặc Tab, để chuyển tiêu điểm sang danh sách mục của danh mục đó
* Nhấp chuột phải, hoặc nhấn phím Application/Menu, để mở menu ngữ cảnh. Nội dung menu phụ thuộc vào thứ đang chọn: nút danh mục hiển thị các tùy chọn quản lý danh mục (Thêm/Đổi tên/Xóa/Di chuyển), còn nút mặc định chỉ hiển thị "Add Category" (Thêm danh mục)

Khi tiêu điểm đang ở danh sách mục (bên phải), nhấp chuột phải hoặc nhấn phím Application/Menu để mở menu Hành động (Action) dùng chung trong toàn add-on (Xem thông tin video, Bình luận, Tải xuống, Thêm vào..., v.v.). Menu này khác với menu ngữ cảnh của cây danh mục.

Cắt, Sao chép và Dán trên danh sách mục hoạt động như đã mô tả ở trên, và khi dán, các mục luôn được đặt vào danh mục đang chọn trong cây.

#### Sắp xếp (Sorting)

Nút **Sort... (Alt+O)** có ở mọi thẻ có danh sách sắp xếp được, gồm Video, Watch List và Search History. Nút này mở một hộp thoại với các tùy chọn:

* **Sort by (Sắp xếp theo):** trường dùng để sắp xếp (Tiêu đề, Kênh, Thời lượng, Ngày đăng, Ngày thêm; các trường có khác nhau đôi chút tùy thẻ)
* **Ascending / Descending (Tăng dần / Giảm dần)**
* **Sort only the current category (Chỉ sắp xếp danh mục hiện tại):** khi chọn, việc sắp xếp chỉ đổi thứ tự các mục trong danh mục đang chọn ở cây, các danh mục khác giữ nguyên. Mặc định không chọn, nghĩa là việc sắp xếp áp dụng cho tất cả danh mục cùng lúc.
* **Apply permanently (saves to file) (Áp dụng vĩnh viễn, lưu vào file):** khi chọn, thứ tự mới được ghi vào ổ đĩa ngay lập tức. Khi không chọn, việc sắp xếp chỉ là tạm thời: nó thay đổi những gì bạn thấy lúc này nhưng sẽ trở lại như cũ ở lần tải lại danh sách hoặc lần tìm kiếm tiếp theo.
* **Clear Sort (Xóa sắp xếp):** hủy mọi sắp xếp tạm thời và khôi phục thứ tự đã lưu trên ổ đĩa.

#### Danh sách video

Ở thẻ Video và Watch List, cũng như mọi màn hình khác hiển thị danh sách video, bạn sẽ thấy hai nút **Action...** (Hành động) và **Copy...** (Sao chép). Đây là các điều khiển chuẩn trong mọi danh sách video. Riêng nguồn cấp đăng ký có thêm tùy chọn "Unsubscribe from this channel" (Hủy đăng ký kênh này).

Nhấn Enter trên một mục để mở video trong trình duyệt, hoặc nhấn phím Space để thực hiện Hành động nhanh (Quick Action), mà bạn có thể đặt trong phần [Cài đặt](#cài-đặt).

##### Nút Action (Hành động)

Nhấn Alt+A để mở menu Hành động, gồm:

* Xem thông tin video... (View Video Info) (i)
* Xem bình luận / Phát lại... (View Comments / Replay) (c)
* Xem chương/mốc thời gian... (View Chapters/Timestamps) (t)
* Mô tả ảnh thu nhỏ (Be My Eyes)... (Get Thumbnail Description) (g)
* Tải video (Download Video) (d)
* Tải âm thanh (Download Audio) (a)
* Thêm vào Video yêu thích (Add to Favorite Videos) (f)
* Thêm vào Kênh yêu thích (Add to Favorite Channels) (f)
* Thêm vào Danh sách xem sau (Add to Watch List) (w)
* Mở video trong trình duyệt (Open video in browser) (b)
* Mở kênh trong trình duyệt (Open channel in browser) (h)
* Hiện video của kênh (Show channel videos) (v)
* Hiện shorts của kênh (Show channel shorts) (s)
* Hiện live của kênh (Show channel live) (l)
* Hiện danh sách phát của kênh (Show channel playlist) (l)
* Hiện podcast của kênh (Show channel podcast) (p)

##### Nút Copy (Sao chép)

Nhấn Alt+C để mở menu Sao chép, gồm:

* Sao chép tiêu đề (Copy Title) (t)
* Sao chép URL video (Copy Video URL) (u)
* Sao chép tên kênh (Copy Channel Name) (c)
* Sao chép URL kênh (Copy Channel URL) (h)
* Sao chép tóm tắt (Copy Summary) (s)

### Nguồn cấp đăng ký (Subscription feed)

Cửa sổ hiển thị video từ các kênh bạn theo dõi trong add-on. Phần này tách biệt với danh sách đăng ký trong tài khoản YouTube của bạn, nên không cần liên kết tài khoản hay cung cấp dữ liệu cá nhân.

Khác với cửa sổ Yêu thích, màn hình này dùng các thẻ chuẩn chia theo loại nội dung:

* **All (Tất cả):** gộp mọi loại nội dung
* **Video:** chỉ video thường
* **Shorts:** chỉ video ngắn
* **Live:** các buổi phát trực tiếp và bản phát lại của chúng

Ngoài các danh mục mặc định này, bạn có thể tạo danh mục tùy chỉnh và cấu hình kênh nào sẽ xuất hiện trong danh mục nào.

#### Các lệnh trong nguồn cấp đăng ký

* Nhấn Control+1 đến Control+0 để nhảy đến thẻ danh mục (tối đa 10 danh mục)
* Nhấn Control+Lên/Xuống để đổi thứ tự danh mục, giống như trong cửa sổ Yêu thích
* Nhấn F2 để đổi tên danh mục (trừ 4 danh mục mặc định)
* Nhấn Control+= để thêm danh mục mới
* Nhấn Control+- để xóa danh mục (trừ 4 danh mục mặc định)
* Dùng các nút Action và Copy của từng video, hoặc nhấn Enter để mở video trong trình duyệt
* Nhấn Delete hoặc Alt+S để đánh dấu video là đã xem. Video đó sẽ bị xóa khỏi danh sách
* Nhấn Control+Delete để đánh dấu tất cả video trong thẻ hiện tại là đã xem

Các nút bổ sung trong cửa sổ này:

* **Mark as seen (Alt+S) (Đánh dấu đã xem):** xóa video khỏi danh sách; phím Delete cũng có tác dụng tương tự
* **Add new Subscription from clipboard URL (Alt+N) (Thêm đăng ký mới từ URL trong clipboard):** đăng ký một kênh bằng URL đã sao chép vào clipboard
* **Update Feed (Alt+U) (Cập nhật nguồn cấp):** cập nhật thủ công tất cả các kênh đã đăng ký. Theo mặc định, add-on cũng tự cập nhật mỗi khi NVDA khởi động
* **More... (Alt+M) (Thêm...):** mở menu con với các tùy chọn bổ sung:
    * Đánh dấu tất cả trong thẻ hiện tại là đã xem (Ctrl+Delete) (a)
    * Hiện tất cả video (kể cả đã xem) (v): chuyển đổi giữa chỉ hiện video chưa xem và hiện tất cả; thiết lập này được lưu tự động
    * Quản lý đăng ký... (m)
    * Thêm danh mục mới... Ctrl+= (c)
    * Đổi tên danh mục hiện tại... F2 (r)
    * Xóa danh mục hiện tại... Ctrl+-
    * Xóa toàn bộ video trong nguồn cấp... (Clear All Feed Videos): xóa mọi video khỏi cơ sở dữ liệu mà không hủy các đăng ký của bạn. Hữu ích khi cơ sở dữ liệu quá lớn và làm NVDA chạy chậm

### Quản lý đăng ký (Manage subscription)

Cửa sổ này hiển thị tất cả các kênh bạn đã đăng ký. Phần đầu tiên là danh sách kênh, tiếp theo là các tùy chọn quản lý cho từng kênh:

* **Filter by Category (Lọc theo danh mục):** lọc danh sách kênh theo danh mục; mặc định là "All"
* **Assign to Categories (Gán vào danh mục):** chọn những danh mục mà nội dung của kênh này sẽ xuất hiện
* **Content Types to Fetch (Loại nội dung cần tải):** chọn loại nội dung sẽ được cập nhật cho kênh này (Videos, Shorts, Live). Hữu ích với những kênh chỉ đăng một số loại nhất định
* **View Content... (Alt+C) (Xem nội dung...):** duyệt nội dung của kênh, giống nút Action
* **Add new subscribe channel from Clipboard... (Alt+N) (Đăng ký kênh mới từ clipboard...):** đăng ký một kênh mới bằng URL trong clipboard
* **Unsubscribe from this Channel (Alt+U) (Hủy đăng ký kênh này):** xóa kênh khỏi danh sách đăng ký của bạn
* **Save Changes (Lưu thay đổi):** **quan trọng:** bạn phải nhấn nút này trước khi đóng cửa sổ, nếu không các thay đổi sẽ không được lưu

### Trình quản lý hồ sơ người dùng (User Profile Manager)

Cửa sổ này dùng để quản lý các hồ sơ người dùng. Add-on có sẵn một hồ sơ "default" (mặc định). Tại đây bạn có thể thêm, xóa hoặc đổi tên hồ sơ. Để chuyển qua lại giữa các hồ sơ, hãy vào bảng Cài đặt của add-on.

Trong cửa sổ này:

* Nhấn F2 để đổi tên hồ sơ đang chọn
* Nhấn Delete để xóa hồ sơ đang chọn

**Lưu ý:** Xóa một hồ sơ sẽ xóa vĩnh viễn toàn bộ dữ liệu gắn với hồ sơ đó. Mọi video, kênh hoặc đăng ký đã lưu trong hồ sơ ấy sẽ bị mất.

### l: (xem bình luận)

Có ba loại bình luận trên video YouTube:

* **Comment (Bình luận):** bình luận thông thường của người xem trên video thường
* **Live chat (Trò chuyện trực tiếp):** các tin nhắn được gửi trong lúc phát trực tiếp
* **Live chat replay (Phát lại live chat):** đoạn live chat đã ghi lại của một video từng phát trực tiếp, nếu chủ kênh chưa xóa nó

YoutubePlus hỗ trợ truy cập cả ba loại này thông qua lệnh này.

#### Live chat của...

Với video đang phát trực tiếp, nhấn L và add-on sẽ mở một cửa sổ mới hiển thị các tin nhắn chat đến. Chỉ những tin nhắn nhận được sau khi bạn kích hoạt lệnh mới được hiển thị. Các tin nhắn trước đó không được ghi lại.

Bạn có thể đóng cửa sổ này và mở lại sau bằng lệnh V trong lớp YoutubePlus, miễn là buổi phát vẫn đang diễn ra và NVDA chưa được khởi động lại.

Dùng lệnh R để bật hoặc tắt việc NVDA đọc to các tin nhắn mới khi chúng đến. Cách này phù hợp với các buổi phát có ít tin nhắn. Với các buổi phát có nhiều tin nhắn, tắt tự động đọc và tự cuộn xem trong cửa sổ sẽ dễ hơn.

Nhấn Shift+L để dừng theo dõi chat của video hiện tại.

Ba thiết lập ảnh hưởng trực tiếp đến tính năng này:

- **Automatically speak incoming live chat (Tự động đọc live chat đến):** Khi được chọn, NVDA đọc to các tin nhắn mới ngay lập tức. Chức năng giống lệnh R, nhưng được lưu làm tùy chọn mặc định.
- **Live chat refresh interval (Khoảng thời gian làm mới live chat):** Tần suất (tính bằng giây) add-on kiểm tra tin nhắn mới. Mặc định là 5 giây.
- **Message history limit (Giới hạn lịch sử tin nhắn):** Số tin nhắn tối đa được lưu trong bộ nhớ trong một phiên. Cửa sổ live chat chỉ hiển thị các tin nhắn gần nhất, tối đa bằng giới hạn này (mặc định: 5.000). Add-on vẫn giữ toàn bộ tin nhắn ở chế độ nền để xuất ra file, với mức tối đa 200.000 tin để tránh dùng quá nhiều bộ nhớ.

Khi buổi phát kết thúc, hoặc khi add-on phát hiện nó đã kết thúc, một hộp thoại sẽ tự động hiện ra hỏi bạn có muốn xuất toàn bộ tin nhắn đã thu thập không. Nhấn Yes (Có) để lưu lịch sử chat thành một file.

#### Bình luận / Phát lại live chat

Với video thường đã đăng hoặc các buổi phát đã lưu trữ, bạn truy cập bình luận theo cách tương tự. Nếu có cả bản phát lại live chat lẫn bình luận thông thường, một hộp thoại sẽ hỏi bạn muốn tải loại nào.

Số lượng bình luận hiển thị không bị giới hạn, tuy nhiên việc tải có thể mất thời gian với video có nhiều bình luận.

Bình luận được hiển thị với các bình luận được ghim ở đầu, tiếp theo là tất cả bình luận còn lại theo thứ tự sắp xếp đã cấu hình trong Cài đặt (mới nhất trước hoặc cũ nhất trước).

#### Các phần của cửa sổ bình luận

* **Search field (Ô tìm kiếm):** gõ để lọc bình luận; kết quả cập nhật ngay lập tức
* **Filter combo box (Hộp chọn bộ lọc):** chọn một tùy chọn lọc (add-on tự điền vào ô tìm kiếm):
    * No Filter (Không lọc): mặc định; hiển thị tất cả bình luận
    * Filter by Selected Author (Lọc theo tác giả đang chọn): chỉ hiển thị bình luận của người bình luận đang chọn
    * Show Super Chats Only (Chỉ hiện Super Chat)
    * Show Super Stickers Only (Chỉ hiện Super Sticker)
    * Show Super Thanks Only (Chỉ hiện Super Thanks)
* **Comment list (Danh sách bình luận):** hiển thị tên người bình luận, theo sau là nội dung
* **Read-only text area (Vùng văn bản chỉ đọc):** cuộn để đọc toàn bộ nội dung bình luận đang chọn, hữu ích khi bình luận quá dài không hiển thị đủ trong danh sách
* **Copy button (Alt+C hoặc Ctrl+C) (Nút Sao chép):** sao chép bình luận đang chọn
* **Export button (Alt+E) (Nút Xuất):** lưu tất cả bình luận thành file văn bản trong thư mục đã đặt ở phần Cài đặt
* **Total paid amount field (Ô tổng số tiền ủng hộ):** chỉ hiển thị với bản phát lại live chat; cho biết tổng số tiền người xem đã ủng hộ trong buổi phát

## Cài đặt

Mở cài đặt qua `NVDA -> Tùy chọn (Preferences) -> Cài đặt (Settings)...` rồi chọn nhóm **"YoutubePlus"**.

- **Active Profile (Hồ sơ đang dùng):** Chọn hồ sơ muốn sử dụng. Cần khởi động lại sau khi đổi hồ sơ.
- **Manage Profile button (Nút quản lý hồ sơ):** Mở cửa sổ Trình quản lý hồ sơ người dùng.
- **Quick Action (Space bar) (Hành động nhanh, phím Space):** Chọn việc phím Space sẽ làm trong các cửa sổ danh sách video. Có thể chọn mọi tùy chọn trong menu Hành động.
- **Notification mode (Chế độ thông báo):** Chọn cách add-on báo hiệu các hoạt động chạy nền:
  - *Beep (Tiếng bíp):* Âm bíp ngắn
  - *Sound (Âm thanh):* Hiệu ứng âm thanh
  - *Silent (Im lặng):* Không có thông báo bằng âm thanh (NVDA vẫn đọc các phản hồi bằng giọng nói)
- **Default sort order (Thứ tự sắp xếp mặc định):** Chọn sắp xếp các danh sách (bình luận, video của kênh) theo **Newest First** (Mới nhất trước) hay **Oldest First** (Cũ nhất trước).
- **Items to fetch (Số mục cần tải):** Số mục được lấy cho mỗi loại nội dung khi duyệt một kênh, và khi cập nhật nguồn cấp đăng ký. Mặc định: 20.
- **Default content types (Loại nội dung mặc định):** Chọn các loại nội dung sẽ được tải cho kênh mới đăng ký: Videos, Shorts và/hoặc Live.
- **Background update interval (Khoảng thời gian cập nhật nền):** Tần suất add-on kiểm tra nội dung mới từ các kênh đã đăng ký. Có thể tắt, hoặc đặt từ 15 phút đến 24 giờ. Theo mặc định, add-on cũng tự cập nhật mỗi khi NVDA khởi động.
- **Automatically speak incoming live chat (Tự động đọc live chat đến):** Khi được chọn, NVDA đọc to các tin nhắn chat mới ngay khi chúng đến.
- **Live chat refresh interval (Khoảng thời gian làm mới live chat):** Tần suất (tính bằng giây) add-on kiểm tra tin nhắn mới. Mặc định: 5 giây.
- **Message history limit (Giới hạn lịch sử tin nhắn):** Số tin nhắn chat tối đa được lưu trong bộ nhớ trong một phiên.
- **Default subtitle format (Định dạng phụ đề mặc định):** Định dạng file phụ đề khi tải xuống: SRT, VTT, TTML hoặc TXT (văn bản thuần, không có mốc thời gian)
- **Download Quality and Format Options (Alt+D) (Tùy chọn chất lượng và định dạng tải xuống):** Một mục có thể thu gọn/mở rộng (mặc định là thu gọn). Nhấn Alt+D ở bất kỳ đâu trong trang Cài đặt, hoặc kích hoạt trực tiếp mục này, để mở rộng/thu gọn. Mục này gồm:
  - *Preferred video quality (Chất lượng video ưu tiên):* Best available (tốt nhất hiện có), hoặc giới hạn độ phân giải từ 2160p xuống 360p.
  - *Preferred video container (Định dạng chứa video ưu tiên):* MP4, MKV hoặc WebM.
  - *Preferred audio quality (when converting) (Chất lượng âm thanh ưu tiên, khi chuyển đổi):* Best available, hoặc một mức bitrate từ 320 xuống 96 kbps. Chỉ áp dụng khi định dạng âm thanh bên dưới không phải "Best available".
  - *Preferred audio format (Định dạng âm thanh ưu tiên):* Best available (không chuyển đổi, là mặc định: tải đúng định dạng mà YouTube đang cung cấp, không cần FFmpeg), hoặc chuyển đổi sang MP3, WAV, M4A/AAC, FLAC, Opus hoặc Vorbis (OGG). Bất kỳ phép chuyển đổi nào trong số này đều cần FFmpeg, giống như khi tải video.
- **Cookie method (Experimental) (Phương thức cookie, thử nghiệm):** Chọn trình duyệt mà bạn đang đăng nhập YouTube. Add-on sẽ lấy cookie từ trình duyệt đó để xác thực các yêu cầu, điều này có thể giúp khắc phục lỗi "Sign in to confirm you're not a bot" (Đăng nhập để xác nhận bạn không phải là bot). Lưu ý đây là tính năng thử nghiệm, kết quả phụ thuộc vào trình duyệt và cấu hình hệ thống.
- **Default download and export folder path (Thư mục tải xuống và xuất file mặc định):** Thư mục đích cho video/âm thanh đã tải và lịch sử chat đã xuất.
- **Backup data now (Sao lưu dữ liệu ngay):** Sao lưu thủ công toàn bộ dữ liệu của hồ sơ đang dùng. Add-on cũng tự động sao lưu mỗi ngày ở chế độ nền.
- **Restore data from backup (Khôi phục dữ liệu từ bản sao lưu):** Hiển thị danh sách các bản sao lưu hiện có (tối đa 5 ngày gần nhất) để bạn chọn ngày muốn khôi phục.

## Thông tin bổ sung

Add-on này dựa vào hai thư viện chính: [pytchat](https://pypi.org/project/pytchat/) để theo dõi live chat, và [yt-dlp](https://pypi.org/project/yt-dlp/) cho mọi truy cập dữ liệu YouTube khác. Chúng tôi chân thành cảm ơn các nhà phát triển của cả hai thư viện.

### Về yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) là một trong những công cụ mã nguồn mở mạnh nhất để tải video và âm thanh từ các trang web trên khắp thế giới, hỗ trợ hơn 1.000 trang chứ không riêng YouTube. Công cụ này miễn phí, mã nguồn mở, được cộng đồng toàn cầu tích cực duy trì, không có quảng cáo hay phần mềm độc hại như nhiều công cụ tải xuống trên trình duyệt.

Tuy vậy, xin lưu ý các nguyên tắc sử dụng sau:

1. **Sử dụng hợp lý (Fair Use):** Tránh tải lượng lớn dữ liệu hoặc gửi yêu cầu liên tục trong thời gian ngắn. YouTube có thể phát hiện hoạt động bất thường và tạm thời hạn chế truy cập từ địa chỉ IP của bạn.
2. **Bản quyền và quyền riêng tư:** Mọi dữ liệu hoặc nội dung lấy về chỉ nên dùng để xem hoặc phân tích cá nhân. Hãy tôn trọng Điều khoản dịch vụ của từng nền tảng và không sử dụng dữ liệu theo cách vi phạm bản quyền.
3. **Trách nhiệm:** Bạn chịu trách nhiệm về cách mình sử dụng phần mềm này. Nhà phát triển add-on chỉ cung cấp giao diện để truy cập dữ liệu YouTube thông qua thư viện yt-dlp.

**Mẹo:** Nếu cần xử lý lượng dữ liệu lớn, hãy giãn cách các yêu cầu để giữ kết nối ổn định và tránh bị hạn chế truy cập.
