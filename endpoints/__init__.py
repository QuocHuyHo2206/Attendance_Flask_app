import os
import glob

#Thư viện glob hỗ trợ xử lý hàng loạt file
#Bình thường để sử dụng các module thì phải __all__=[student_endpoint, teacher_endpoint] gây mất thời gian
#Câu lệnh hỗ trợ lấy tất cả các file name không lấy đuôi .py để có thể sử dụng
__all__=[os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py" )]