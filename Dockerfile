FROM python:3.10.9-slim

# set the working directory in the container
WORKDIR /conjoint

# copy the current directory contents into the container at /conjoint
COPY conjoint /conjoint

# install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# run the conjoint program when the container launches
CMD ["python", "conjoint.py"]