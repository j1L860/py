from flask import Flask, request, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set the uploads folder for saving files

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return "Error: Please upload both files.", 400

    # Save the uploaded files to the UPLOAD_FOLDER
    file1 = request.files['file1']
    file2 = request.files['file2']
    filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], 'FileS.txt')
    filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], 'File3_2.txt')
    file1.save(filepath1)
    file2.save(filepath2)

    # Load the data into DataFrames
    sample_data = pd.read_csv(filepath1)
    reference_data = pd.read_csv(filepath2)

    # Step 3: Compare SNPs to identify haplogroup matches
    results = []
    for index, row in sample_data.iterrows():
        position = row['POSITION']
        result = row['RESULT']
        second_nucleotide = result[1] if len(result) > 1 else result

        ref_row = reference_data[reference_data['POSITION'] == position]
        if not ref_row.empty:
            ref_allele = ref_row['RESULT'].values[0]
            match_status = 'positive' if second_nucleotide in ref_allele else 'negative'
            haplogroup = ref_row['HAPLOGROUP'].values[0]
            results.append((position, match_status, haplogroup))

    results_df = pd.DataFrame(results, columns=['POSITION', 'STATUS', 'HAPLOGROUP'])
    positive_snps_count = results_df[results_df['STATUS'] == 'positive'].shape[0]

    # Step 7: Create the bar chart visualization
    haplogroup_status = results_df.groupby(['HAPLOGROUP', 'STATUS']).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 6))
    haplogroup_status.plot(kind='bar', stacked=True, color=['red', 'green'])
    plt.xlabel('Haplogroup')
    plt.ylabel('Number of SNPs')
    plt.title('Haplogroup Confirmation Results (Second Nucleotide Match)')
    plt.legend(['Negative', 'Positive'])

    # Save the plot to the uploads folder
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_plot.png')
    plt.savefig(plot_path)
    plt.close()

    return render_template('index.html', positive_snps_count=positive_snps_count, plot_url=plot_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve the uploaded file (including the plot) from the uploads folder
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
