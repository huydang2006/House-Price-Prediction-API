from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


# Task 1: Prediction function 
def predict_price(area: float, bedrooms: int, location: str) -> float:
    price = 500_000_000.0
    price += area * 15_000_000
    price += bedrooms * 50_000_000

    location = location.lower()
    if location == "hanoi":
        price *= 1.3
    elif location == "hcmc":
        price *= 1.25

    price = round(price / 1_000_000) * 1_000_000
    return price


# Task 2: turn that function into a GET endpoint
'''
Using plain "def" (not "async def") because predict_price() is just
fast Python math -- there's nothing to "wait" on, so async gives us
no benefit here.
'''
@app.get("/predict")
def get_predict(area: float, bedrooms: int, location: str = "other"):
    predicted_price = predict_price(area, bedrooms, location)
    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predicted_price,
    }


# Task 4: serve house_form.html from this same FastAPI app.
app.mount("/static", StaticFiles(directory="../frontend"), name="static")