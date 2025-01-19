#!/usr/bin/env python3
import pgnull

game = pgnull.Game()

WIDTH = 1280
HEIGHT = 720

game.open_screen(WIDTH, HEIGHT)

@game.event("on_update")
def update(context):
    game.screen.fill("dim grey")
    game.screen.draw_rect(main_box, "sky blue")
    game.screen.draw_rect(timer_box, "sky blue")
    game.screen.draw_textbox("69", timer_box, fontsize=45)
    for box in answer_boxes:
        game.screen.draw_rect(box, "orange")

@game.event("on_mouse_down")
def on_mouse_down(pos, button):
    if button ==  1:
        for i, box in enumerate(answer_boxes):
            if box.collidepoint(pos):
                print("clicked ans", i)

main_box = pgnull.Rect(50, 40, 820, 240)
timer_box = pgnull.Rect(990, 40, 240, 240)
answer_box1 = pgnull.Rect(50, 358, 495, 165)
answer_box2 = pgnull.Rect(735, 358, 495, 165)
answer_box3 = pgnull.Rect(50, 538, 495, 165)
answer_box4 = pgnull.Rect(735, 538, 495, 165)

answer_boxes = [answer_box1, answer_box2, answer_box3, answer_box4]

if __name__ == '__main__':
    game.run_game()
