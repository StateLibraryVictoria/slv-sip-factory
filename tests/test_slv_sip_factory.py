import os
from src.slv_sip_factory import SlvSipFactory
from conftest import COMMON_BAG_UUID


def test_slv_sip_factory_compiles_events(transfer_df, big_validation_df):
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    events = factory.compile_events(COMMON_BAG_UUID)
    assert len(events) == 4


def test_slv_sip_factory_creates_sips_from_json_multi_ark(
    report_for_transfer_1_multiple_arks,
    SC_transfer_1,
    tmp_path,
    transfer_df,
    big_validation_df,
):
    uuid = "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0"
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    output_dir = tmp_path / "folder"
    output_dir.mkdir()
    print(output_dir)
    factory.build_sip_from_manifest(
        bag_uuid=uuid,
        input_dir=SC_transfer_1,
        output_dir=output_dir,
        sip_title="test-sip",
        transfer_manifest=report_for_transfer_1_multiple_arks,
    )
    transfer_count = len(os.listdir(output_dir))
    assert transfer_count == 4
    transfer_out = os.listdir(output_dir)[0]
    manifest = os.path.join(output_dir, transfer_out, "content", "mets.xml")
    assert os.path.exists(manifest)
    data_files = os.listdir(
        os.path.join(output_dir, transfer_out, "content", "streams")
    )
    assert len(data_files) == 1


def test_slv_sip_factory_creates_sip_from_json(
    report_for_transfer_1_one_ark,
    SC_transfer_1,
    tmp_path,
    transfer_df,
    big_validation_df,
):
    uuid = "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0"
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    output_dir = tmp_path / "folder"
    output_dir.mkdir()
    factory.build_sip_from_manifest(
        bag_uuid=uuid,
        input_dir=SC_transfer_1,
        output_dir=output_dir,
        sip_title="test-sip",
        transfer_manifest=report_for_transfer_1_one_ark,
    )
    transfer_count = len(os.listdir(output_dir))
    assert transfer_count == 1
    transfer_out = os.listdir(output_dir)[0]
    manifest = os.path.join(output_dir, transfer_out, "content", "mets.xml")
    assert os.path.exists(manifest)
    data_files = os.listdir(
        os.path.join(output_dir, transfer_out, "content", "streams")
    )
    assert len(data_files) == 4


def test_slv_sip_factory_creates_sip_with_hierarchy(
    report_for_transfer_2_one_id,
    SC_transfer_2,
    tmp_path,
    transfer_df,
    big_validation_df,
):
    uuid = "7fc12852-05ff-4405-abef-459d24aaa6aa"
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    output_dir = tmp_path / "folder"
    output_dir.mkdir()
    factory.build_sip_from_manifest(
        bag_uuid=uuid,
        input_dir=SC_transfer_2,
        output_dir=output_dir,
        sip_title="test-sip",
        transfer_manifest=report_for_transfer_2_one_id,
    )
    transfer_count = len(os.listdir(output_dir))
    assert transfer_count == 1
    transfer_out = os.listdir(output_dir)[0]
    manifest = os.path.join(output_dir, transfer_out, "content", "mets.xml")
    assert os.path.exists(manifest)
    streams = os.path.join(output_dir, transfer_out, "content", "streams")
    file_count = sum(len(files) for root, dir, files in os.walk(streams))
    assert file_count == 6
