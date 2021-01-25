import asyncio
import json
import logging
import websockets

cards = ["2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "JC", "QC", "KC", "AC", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "JD", "QD", "KD", "AD", "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "JS", "QS", "KS", "AS", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "JH", "QH", "KH", "AH"]

pile = cards.copy()

card_deck = []

USERS = {}

async def broadcast(message):
    print(message)
    if USERS:
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS[websocket] = []
    await broadcast(f"{websocket} has joined")


async def unregister(websocket):
    del USERS[websocket]
    await broadcast(f"{websocket} has left")


async def app(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            split_message = message.split("-")
            print(split_message[0])
            if split_message[0] == "play":
                if split_message[1] in USERS[websocket]:
                    card_deck.append(split_message[1])
                    USERS[websocket].remove(split_message[1])
                    print(card_deck[-1])
                    await broadcast(json.dumps(card_deck))
                else:
                    await broadcast("Card is not in players hand")
            elif split_message[0] == "take":
                print(split_message[1])
                if split_message[1] in pile:
                    USERS[websocket].append(split_message[1])
                    pile.remove(split_message[1])
                    await broadcast("Card " + split_message[1] + " added to players hand.")
                else:
                    await broadcast("Card " + split_message[1] + " is not in the pile.")
    finally:
        await unregister(websocket)


start_server = websockets.serve(app, "localhost", 8203)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
