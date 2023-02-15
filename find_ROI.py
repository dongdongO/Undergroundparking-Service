import cv2

click = False  # Mouse 클릭된 상태 (false = 클릭 x / true = 클릭 o) : 마우스 눌렀을때 true로, 뗏을때 false로
x1, y1 = -1, -1

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
PURPLE = (247, 44, 200)
ORANGE = (44, 162, 247)
MINT = (239, 255, 66)
YELLOW = (2, 255, 250)

roi_list = []


def draw_rectangle(event, x, y, flags, param):
    global x1, y1, click, img
    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스를 누른 상태
        click = True
        x1, y1 = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # 마우스 이동
        if click:
            img_draw = img.copy()
            cv2.rectangle(img_draw, (x1, y1), (x, y), BLUE, 1)
            cv2.imshow('img', img_draw)

    elif event == cv2.EVENT_LBUTTONUP:
        click = False  # 마우스를 때면 상태 변경
        w = x - x1
        h = y - y1
        if w > 0 and h > 0:
            cv2.rectangle(img, (x1, y1), (x, y), BLUE, 1)
            rectan = [x1, y1, x, y]
        else:
            print('왼쪽 위에서 오른쪽 아래로 드래그 하세요.')
        print(rectan)
        roi_list.append(rectan)
        print(roi_list)


img = cv2.imread("./runs/detect/exp/images/CCTV23.jpg")
# img = cv2.resize(img, dsize=(1920, 1080), interpolation=cv2.INTER_AREA)
# 이미지 표시 창의 크기 및 위치 조정 (resize가 비활성화되면 원본 이미지 크기대로 좌표값 설정)
cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.resizeWindow('img', 1600, 900)
cv2.moveWindow('img', 0, 0)
cv2.imshow('img', img)
cv2.setMouseCallback('img', draw_rectangle)  # 마우스 이벤트 후 callback 수행하는 함수 지정
cv2.waitKey(0)
cv2.destroyAllWindows()
