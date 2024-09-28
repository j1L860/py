from flask import Flask, request, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Path to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if files are uploaded
    if 'sample_file' not in request.files or 'reference_file' not in request.files:
        return "Error: Missing files", 400

    sample_file = request.files['sample_file']
    reference_file = request.files['reference_file']

    # Save the files to the upload folder
    sample_filepath = os.path.join(UPLOAD_FOLDER, sample_file.filename)
    reference_filepath = os.path.join(UPLOAD_FOLDER, reference_file.filename)
    sample_file.save(sample_filepath)
    reference_file.save(reference_filepath)

    # Process the uploaded files
    sample_data = pd.read_csv(sample_filepath)
    reference_data = pd.read_csv(reference_filepath)

    # Compare SNPs (as per your original logic)
    results = []
    for _, row in sample_data.iterrows():
        position = row['POSITION']
        result = row['RESULT']

        if len(result) > 1:
            second_nucleotide = result[1]
        else:
            second_nucleotide = result

        ref_row = reference_data[reference_data['POSITION'] == position]
        if not ref_row.empty:
            ref_allele = ref_row['RESULT'].values[0][1]
            if second_nucleotide == '-':
                match_status = 'U*'
            elif second_nucleotide == ref_allele:
                match_status = 'P+'
            else:
                match_status = 'N-'
            haplogroup = ref_row['HAPLOGROUP'].values[0]
            results.append((position, match_status, haplogroup))

    results_df = pd.DataFrame(results, columns=['POSITION', 'STATUS', 'HAPLOGROUP'])

    # Plot the results
    haplogroup_status = results_df.groupby(['HAPLOGROUP', 'STATUS']).size().unstack(fill_value=0)
    plot_filepath = os.path.join(UPLOAD_FOLDER, 'haplogroup_plot.png')
    haplogroup_status.plot(kind='bar', stacked=True, color=['red', 'green', 'gray'], figsize=(6, 4))
    plt.xlabel('Haplogroup')
    plt.ylabel('Number of SNPs')
    plt.title('Haplogroup Confirmation Results')
    plt.legend(['N-', 'P+', 'U*'])
    plt.savefig(plot_filepath)
    plt.close()

    return render_template('results.html', plot_url=plot_filepath)

if __name__ == '__main__':
    app.run(debug=True)
