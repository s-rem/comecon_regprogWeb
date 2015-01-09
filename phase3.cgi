#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use warnings;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use MIME::Base64;
use SFCON::Register;
use SFCON::Register_db;
use Encode::Guess qw/ shiftjis euc-jp 7bit-jis /;
use Encode qw/ encode decode from_to/;
use pgreglib;
our %CONDEF_CONST;

my $cgi=CGI->new;
my $register = SFCON::Register->new;
my $database = SFCON::Register_db->new;

# セッションID = urlパラメータ||cookieからCGISESSID||取得できなかったらundef．
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page;
my $http_header;

if(defined $sid && $sid eq $session->id){
    # 取得したセッションidが有効:登録処理
    ##>> テストDB使用
    $database->prefix("test54_");
    ##<< テストDB使用
	my $r_num = sprintf( "%04d", $database->getprogramnumber($session->id, 0));
    my $name     = $session->param('p1_name');
	my $mailaddr = $session->param('email');

	# 登録者に送るmail生成/送付
	my $mail_out = HTML::Template->new(filename => 'mail-finish-tmpl.txt');
    pgreglib::pg_stdMailTmpl_set( $mail_out, $mailaddr, $name );
    pgreglib::pg_HtmlTmpl_set($mail_out, $session);
    my $mbody = $mail_out->output;
    pgreglib::doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $mailaddr, $CONDEF_CONST{'ENTADDR'}, ],
                $mbody );

	# 企画登録スタッフに送るメールの作成/送付
	$mail_out = HTML::Template->new(filename => 'mail-regist-tmpl.txt');
    pgreglib::pg_stdMailTmpl_set( $mail_out, $CONDEF_CONST{'PGSTAFF'}, undef );
    $mail_out->param(PGNO       => $r_num);
    $mail_out->param(MIMEPGSG   => $CONDEF_CONST{'MIMEPGS'});
    $mail_out->param(MAILBODY   => create_reg_mail_body($session, $r_num));
    my $mbody2 = $mail_out->output;
    pgreglib::doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $CONDEF_CONST{'PGSTAFF'}, ],
                $mbody2 );
	
	# HTMLを生成する。
    $input_page=HTML::Template->new(filename => 'phase3-tmpl.html');
    pgreglib::pg_HtmlTmpl_set($input_page, $session);
    if ( $session->param('reg_num') eq $CONDEF_CONST{'SPREGNUM2'}) {
        pgreglib::pg_HtmlMailChk_set($input_page, $mbody, $mbody2);
    }
	$http_header = $cgi->header(-charset=>'UTF-8', -expires=>'now');

    # 全処理が完了したのでセッションを削除
	$session->close;
  	$session->delete;

}else{
    # 取得したセッションidが無効:エラー画面表示
    # 古いセッションを削除
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
    $input_page=HTML::Template->new(filename => 'error.html');
	$http_header = $cgi->header(-charset=>'UTF-8');
}
# 共通のTMPL変数置き換え
pgreglib::pg_stdHtmlTmpl_set( $input_page, $sid );

print $http_header;
print "\n\n";
print $input_page->output;

exit;

# 企画管理スタッフ宛 兼 企画管理システム登録用メール本文生成
#### JSONかJSONPかYAMLか
sub create_reg_mail_body {
	my ( $session, $pg_num ) = @_;
	my $mail_text = "";

=head 1 name
	my(undef, undef, undef, $c_d, $c_m, $c_y,undef, undef, undef) = localtime(time);
	$c_y += 1900;
	$c_m += 1;
	$mail_text = $mail_text . '"' . $pg_num . '","WEB","","","' . $c_y. '/' . $c_m . '/' . $c_d . '",';

	# 主催者情報
	$mail_text = $mail_text . '"' . strCheck($session->param('p1_name')) . '",';

	$mail_text = $mail_text . '"' . strCheck($session->param('email')) . '","PC",';
	$mail_text = $mail_text . '"' . strCheck($session->param('reg_num')) . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('tel')) . '",';

	$mail_text = $mail_text . '"' . strCheck($session->param('fax')) . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('hp')) . '",';

	# 企画情報
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_name')) . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_name_f')) . '",';
	$mail_text = $mail_text . '"' . $pg_kind_tbl{$session->param('pg_kind')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_kind2')) . '",';
	$mail_text = $mail_text . '"' . $pg_place_tbl{$session->param('pg_place')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_place2')) . '",';
	$mail_text = $mail_text . '"' . $pg_layout_tbl{$session->param('pg_layout')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_layout2')) . '",';
	$mail_text = $mail_text . '"' . $pg_time_tbl{$session->param('pg_time')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_time2')) . '",';
	$mail_text = $mail_text . '"' . $pg_koma_tbl{$session->param('pg_koma')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_koma2')) . '",';
	$mail_text = $mail_text . '"' . $pg_ninzu_tbl{$session->param('pg_ninzu')} . '",';
	$mail_text = $mail_text . '"' . $pg_naiyou_k_tbl{$session->param('pg_naiyou_k')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_naiyou')) . '",';
	$mail_text = $mail_text . '"' . $pg_kiroku_kb_tbl{$session->param('pg_kiroku_kb')} . '",';
	$mail_text = $mail_text . '"' . $pg_kiroku_ka_tbl{$session->param('pg_kiroku_kb')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_wb_tbl{$session->param('fc_wb')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_mic_a_tbl{$session->param('fc_mic_a')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_mic_b_tbl{$session->param('fc_mic_b')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_vid_tbl{$session->param('fc_vid')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_pc_tbl{$session->param('fc_pc')} . '",';
	$mail_text = $mail_text . '"' . $pg_fc_inet_tbl{$session->param('fc_inet')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('fc_naiyou')) . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('fc_mochikomi')) . '",';
	$mail_text = $mail_text . '"' . $pg_enquete_tbl{$session->param('pg_enquete')} . '",';
	$mail_text = $mail_text . '"' . strCheck($session->param('pg_badprog')) . '",';

	# 出演者情報
	for (my $i = 1; $i <= 8; $i++) {	# CONST: 出演者の最大値
		$mail_text = $mail_text . '"' . strCheck($session->param('pp' . $i . '_name')) . '",';
		$mail_text = $mail_text . '"' . strCheck($session->param('pp' . $i . '_name_f')) . '",';
		$mail_text = $mail_text . '"' . $pg_ppn_con_tbl{$session->param('pp' . $i . '_con')} . '",';
		$mail_text = $mail_text . '"' . $pg_ppn_grq_tbl{$session->param('pp'. $i . '_grq')} . '",';
	}

	$mail_text = $mail_text . '"' . strCheck($session->param('fc_comment')) . '"';

	$mail_text = $mail_text . "\n";
=cut
	return($mail_text);
}

# 不正なキャラを削除して返す
sub	strCheck {
	my ($str) = @_;

	$str =~ s/\r\n/_/g;	# 改行の削除
	$str =~ s/\"/\'/g;	# " の削除
	return($str);
}

1;
#end
