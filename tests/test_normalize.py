from epstein_network.normalize import norm_email,norm_name,extract_emails,stable_id

def test_email_normalization():
    assert norm_email(" <Alice@Example.COM> ")=="alice@example.com"

def test_name_normalization():
    assert norm_name("  Jane   Doe ")=="jane doe"

def test_extract_email():
    assert extract_emails("x A.B+tag@example.org y")==["a.b+tag@example.org"]

def test_stable():
    assert stable_id("x","y")==stable_id("x","y")
