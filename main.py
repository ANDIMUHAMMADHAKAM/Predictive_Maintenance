from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pickle
from dateutil.relativedelta import relativedelta
from datetime import datetime

app = Flask(__name__)

def load_model(model_name):
    with open(f'model/{model_name}.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

###### LOAD MODEL ######
# Model Absorber
data_absorber = load_model('absorber')
model_absorber = data_absorber["model"]
le_area_absorber = data_absorber["le_area"]
le_vehicle_absorber = data_absorber["le_vehicle"]
le_jenis_absorber = data_absorber["le_jenis"]

# Model Wiper
data_wiper = load_model('wiper')
model_wiper = data_wiper["model"]
le_area_wiper = data_wiper["le_area"]
le_vehicle_wiper = data_wiper["le_vehicle"]
le_jenis_wiper = data_wiper["le_jenis"]

# Model Battery
data_battery = load_model('battery')
model_battery = data_battery["model"]
le_area_battery = data_battery["le_area"]
le_vehicle_battery = data_battery["le_vehicle"]
le_jenis_battery = data_battery["le_jenis"]

# Model Brake
data_brake = load_model('brake')
model_brake = data_brake["model"]
le_area_brake = data_brake["le_area"]
le_vehicle_brake = data_brake["le_vehicle"]
le_jenis_brake = data_brake["le_jenis"]

# Model Clutch
data_clutch = load_model('clutch')
model_clutch = data_clutch["model"]
le_area_clutch = data_clutch["le_area"]
le_vehicle_clutch = data_clutch["le_vehicle"]
le_jenis_clutch = data_clutch["le_jenis"]

# Area, Vehicle, and Jenis options
Area = (
    'BAU-BAU', 'BONE', 'BULUKUMBA', 'GOWA', 'KENDARI', 'KOLAKA',
    'LUWUK BANGGAI', 'MAKASSAR', 'MALILI', 'MAMUJU', 'MAROS',
    'PALOPO', 'PALU', 'PARE-PARE', 'POLMAN', 'POSO', 'SENGKANG',
    'SIDRAP', 'SOPPENG', 'TATOR'
)

Vehicle_absorber = (
    'AGYA', 'ALPHARD', 'AVANZA', 'CALYA', 'CAMRY', 'COROLLA',
    'ETIOS', 'FORTUNER', 'FT 86', 'HILUX', 'INNOVA', 'KIJANG',
    'RAIZE', 'RUSH', 'SIENTA', 'VELOZ', 'VIOS', 'YARIS', 'Other'
)

Vehicle_wiper = Vehicle_absorber + ('C-HR', 'DYNA', 'HIACE', 'LANDCRUISER', 'NAV1', 'VELLFIRE')

Vehicle_battery = Vehicle_wiper + ('HARRIER', 'LIMO', 'VOXY')

Vehicle_brake = Vehicle_battery

Vehicle_clutch = Vehicle_absorber

Jenis_absorber = ('Absorber Belakang', 'Absorber Depan', 'Bracket Absorber', 'Karet Dudukan Absorber')
Jenis_wiper = ('Wiper Bagian depan', 'Wiper MVP', 'Karet Wiper', 'Belakang Wiper', 'Lengan Wiper')
Jenis_battery = ('Basah', 'Kering')
Jenis_brake = ('Kampas Rem Belakang', 'Kampas Rem Depan')
Jenis_clutch = ('Kopling tipe MVP', 'Kopling tipe non MVP')

def mileage(x):
    if x >= 105000:
        return 21 + (x - 105000) // 5000
    else:
        return min(x // 5000, 21)

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    return render_template("home.html", title="Home")

def predict_replacement(model, le_area, le_vehicle, le_jenis, area_input, vehicle_input, cmr, age, jenis_input, delivery_date):
    X = np.array([[area_input, vehicle_input, cmr, age, jenis_input]])
    X[:, 0] = le_area.transform(X[:, 0])
    X[:, 1] = le_vehicle.transform(X[:, 1])
    vectorized_mileage = np.vectorize(mileage)
    X[:, 2] = vectorized_mileage(X[:, 2].astype(int))
    X[:, 4] = le_jenis.transform(X[:, 4])
    X = X.astype(int)

    Rentang = model.predict(X)
    Rentang = np.abs(np.round(Rentang)).astype(int)

    delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d")
    months_to_add = Rentang[0]

    replacement_dates = []
    current_date = datetime.now()
    while delivery_date <= current_date:
        replacement_dates.append(delivery_date.strftime('%Y-%m-%d'))
        delivery_date += relativedelta(months=months_to_add)

    future_replacement_dates = []
    while delivery_date <= current_date + relativedelta(months=months_to_add):
        future_replacement_dates.append(delivery_date.strftime('%Y-%m-%d'))
        delivery_date += relativedelta(months=months_to_add)

    return replacement_dates, future_replacement_dates, months_to_add


@app.route("/absorber", methods=["GET", "POST"])
def absorber():
    if request.method == "POST":
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        replacement_dates, future_replacement_dates, months_to_add = predict_replacement(
            model_absorber, le_area_absorber, le_vehicle_absorber, le_jenis_absorber,
            Area_input, Vehicle_input, CMR, Age, Jenis_input, delivery_date
        )

        return render_template("absorber.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle_absorber, 
                               jenis_absorber=Jenis_absorber,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=delivery_date)

    return render_template("absorber.html", areas=Area, vehicles=Vehicle_absorber, jenis_absorber=Jenis_absorber, title="Prediksi Penggantian Absorber")


@app.route("/wiper", methods=["GET", "POST"])
def wiper():
    if request.method == "POST":
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        replacement_dates, future_replacement_dates, months_to_add = predict_replacement(
            model_wiper, le_area_wiper, le_vehicle_wiper, le_jenis_wiper,
            Area_input, Vehicle_input, CMR, Age, Jenis_input, delivery_date
        )

        return render_template("wiper.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle_wiper, 
                               jenis_wiper=Jenis_wiper,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=delivery_date)

    return render_template("wiper.html", areas=Area, vehicles=Vehicle_wiper, jenis_wiper=Jenis_wiper, title="Prediksi Penggantian Wiper")


@app.route("/battery", methods=["GET", "POST"])
def battery():
    if request.method == "POST":
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        replacement_dates, future_replacement_dates, months_to_add = predict_replacement(
            model_battery, le_area_battery, le_vehicle_battery, le_jenis_battery,
            Area_input, Vehicle_input, CMR, Age, Jenis_input, delivery_date
        )

        return render_template("battery.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle_battery, 
                               jenis_battery=Jenis_battery,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=delivery_date)

    return render_template("battery.html", areas=Area, vehicles=Vehicle_battery, jenis_battery=Jenis_battery, title="Prediksi Penggantian Aki")



@app.route("/brake", methods=["GET", "POST"])
def brake():
    if request.method == "POST":
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        replacement_dates, future_replacement_dates, months_to_add = predict_replacement(
            model_brake, le_area_brake, le_vehicle_brake, le_jenis_brake,
            Area_input, Vehicle_input, CMR, Age, Jenis_input, delivery_date
        )

        return render_template("brake.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle_brake, 
                               jenis_brake=Jenis_brake,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=delivery_date)

    return render_template("brake.html", areas=Area, vehicles=Vehicle_brake, jenis_brake=Jenis_brake,
                           title="Prediksi Penggantian Kampas Rem")


@app.route("/clutch", methods=["GET", "POST"])
def clutch():
    if request.method == "POST":
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        replacement_dates, future_replacement_dates, months_to_add = predict_replacement(
            model_clutch, le_area_clutch, le_vehicle_clutch, le_jenis_clutch,
            Area_input, Vehicle_input, CMR, Age, Jenis_input, delivery_date
        )

        return render_template("clutch.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle_clutch, 
                               jenis_clutch=Jenis_clutch,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=delivery_date)

    return render_template("clutch.html", areas=Area, vehicles=Vehicle_clutch, jenis_clutch=Jenis_clutch,
                           title="Prediksi Penggantian Kopling")

if __name__ == "__main__":
    app.run(debug=True)